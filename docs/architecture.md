# Architektur Sequence Cartography

Stand: 2026-11-10 · Grundlage: [Bauauftrag](spec/Bauprompt_Sequenzrolle_und_Leseseite.md), Code von Video Score ([Herkunft](upstream/PROVENANCE.md))

Rahmenbedingungen:

- Sequence Cartography wird **keine BIBBOX-App** mehr. Die BIBBOX-Dateien (`appinfo.json`, `portinfo.json`, `sys-info.json`, `environment-parameters.json`, `file_structure.json`, `INSTALL-APP.md`, `docker-compose-template.yml`) bleiben nur als Historie und werden mit dem Umbau entfernt.
- Entwickelt wird auf einem **Linux-Server**, alle Dienste laufen in Containern. Der Mac dient nur noch als Editor und Browser.

## 1. Bestandsaufnahme Video Score

### 1.1 Laufzeit

| Container | Inhalt | Zustand |
|---|---|---|
| `bibbox-video-score-nginx` | liefert `client/dist` aus, leitet `/api` und `/stream` (SSE) an Flask weiter, `/static` = `data/movies` | lauffähig |
| `bibbox-video-score-server` | Flask 1.0 unter uwsgi, Python-Code per Volume eingebunden | Image baut nicht mehr (siehe 1.4) |
| `bibbox-video-score-celery` | dasselbe Image, Celery-4.2-Worker | wie Server |
| `bibbox-video-score-celery-monitor` | Flower | fehlerhafte Kommandozeile (`-celery A`) |
| `bibbox-video-score-postgres` | PostgreSQL 9.6 | Version veraltet |
| `bibbox-video-score-redis` | Celery-Broker und SSE-Kanal | ok |
| `bibbox-video-score-adminer` | DB-Oberfläche | ok |
| `bibbox-video-score-data` | busybox-Datencontainer (`volumes_from`) | veraltetes Compose-Muster |

### 1.2 Server (`server/`)

- **Modelle** (`app/models/`): `Movie` (Quelle `FILESYSTEM` oder `YOUTUBE`, Frames, fps, Statusfelder für Stripes, Schnitte und Dokument), `Tag` (Tabelle `frametag`: `movieID`, `fn`, `tag="CUT"`), `Document` (`contentIndex` = JSON-Liste von UUIDs), `ContentElement` (`contentType="movieref"`, `content` = JSON `{movieuuid, s, e, n}`, `e` inklusiv), `User` (Klartext-Passwörter).
- **API** (`app/api/`): `/movies`, `/movie/<id>`, `/movie/<id>/command` (startet Tasks), `/movie/<id>/stripes`, `/movie/<id>/cuts`, `/movie/<id>/frame/<fn>` (Einzelbild per Seek), `/movie/<id>/setparams`, `/documents`, `/document/<id>`, `/tasks`. Es gibt keine Authentifizierung und keine Projektbindung.
- **Tasks** (`app/celerytasks/tasks.py`):
  - `generateStripes` schreibt die mittlere Bildspalte in 1500 Frames breite Kacheln.
  - `computeCuts` nutzt die eingebettete PySceneDetect-Kopie (`app/scenedetect/`, threshold 27, min 15). Die Kopie wurde so umgebaut, dass sie Schnitte direkt als `Tag` in die Datenbank schreibt.
  - `generateDocAndOmImages` steht in `document_generator.py`. Es erzeugt pro Schnittbereich ein `ContentElement` und rendert **Sub-OMIs**: Kacheln von ca. 4 s und 400 px Breite mit 1 Keyframe, 4 Miniaturen und Slit-Scan. Das Video wird dabei in einem sequenziellen Durchlauf gelesen.
  - Fortschritt läuft über `self.update_state` und SSE-Nachrichten (`storeID`/`operation`/`payload`) direkt an den NgRx-Store des Clients.
- **Pfade**: fest verdrahtet auf `/data/movies/...`. Cache-URLs werden per String-Ersetzung zu `static/...`.

### 1.3 Client (`client/`)

Angular 9 mit NgRx (Entities für Movies, Cuts, Tasks und Documents) und Angular Material.

| Komponente | Funktion |
|---|---|
| `movies`, `movie-detail` | Liste und Detailansicht, Tasks starten |
| `stripes` | Canvas mit Stripe-Kacheln und Schnittlinien |
| `document-display` | Dokument mit Split-Ansicht, `contentelement` → `omimage` zeigt Sub-OMIs, Klick setzt Film und Frame im Store; daneben ein YouTube-Player mit fest eingetragener ID |
| `task-list` | laufende Celery-Jobs |
| `sse.service`, `syncstore.service` | SSE-Ereignisse in Store-Updates umsetzen |

Das Menü nennt die geplanten Funktionen: Outline, OM Images, Audio Track, Cut-, Audio- und Bewegungsanalyse, Personen. Umgesetzt sind sie nicht. `client/dist` ist eingecheckt, `nodejs-server/` ist ein ungenutzter Versuch.

### 1.4 Probleme und Risiken

1. **Build**: Das committete `server/Dockerfile` (`python:3.11.6`) kombiniert Python-2-apt-Pakete mit Pins von 2018 (Flask 1.0.2, gevent 1.4, psycopg2 2.6.1) und kompiliert ffmpeg und OpenCV 3.4.2 aus dem Quellcode. Das baut nicht mehr. Abhilfe für M0: [`deploy/revival/`](../deploy/revival/).
2. **YouTube**: `pafy` und `youtube-dl` funktionieren nicht mehr. Laut Bauauftrag werden Anbieterlinks nur noch über einen eigenen Connector unterstützt.
3. **Sicherheit**: `.env` mit DB-Zugang und `seed_db` mit Klartext-Passwörtern sind versioniert (öffentlich, auch upstream). Es gibt keine Authentifizierung, `/static` liefert alle Medien ungeschützt aus, und `/movie/<id>/frame` öffnet für jede Anfrage das Video.
4. **Datenbank**: Das Schema entsteht per `recreate_db` und löscht dabei alle Daten. Migrationen gibt es keine.
5. **Koordinaten**: Gearbeitet wird mit Frame-Nummern. `e` ist inklusiv, fps kommt aus OpenCV und wird als konstant angenommen. Frame-Zeitstempel werden nicht erfasst.
6. **Eingebettetes PySceneDetect**: Analyse und Datenbank sind gekoppelt, und die Kopie ist nicht aktualisierbar.

## 2. Zielarchitektur

```
Browser ──► nginx (gateway) ──► /            client (Angular, statisch)
                    │          ──► /api/v1      api (Flask 3, uwsgi/gunicorn)
                    │          ──► /api/v1/events  SSE (Redis pub/sub)
                    └─ X-Accel-Redirect ◄── api prüft Rechte ─► /protected/ → Materialablage
api ──► PostgreSQL 16 (Alembic-Migrationen)
api ──► Redis ──► worker-* (Celery 5): video | text | sequence (FASTA) | music
worker-* ──► Materialablage (MinIO/S3-kompatibel, lokal: Volume)
```

| Dienst | Technik | Aufgabe |
|---|---|---|
| `gateway` | nginx | Routing, Range-Requests, geschützte Medienauslieferung per `X-Accel-Redirect` (Medien-URLs nur nach Rechteprüfung in der API) |
| `client` | Angular, aktuelle Version mit Standalone-Komponenten und Signals | Atlas, Kreiskarte, Editor, Leseseite. Wiederverwendet werden die Konzepte von `omimage`, `stripes` und `sse.service`. |
| `api` | Flask 3, SQLAlchemy 2, Alembic, Pydantic-Schemas | Projekte, Rollen, Quellen, Sequenzen, Revisionen, Importe, Rechteprüfung |
| `worker-video` | Celery 5, ffmpeg/ffprobe, OpenCV headless, PySceneDetect (aktuell, nicht eingebettet) | Probe, Frame-Zeitstempel, Proxy, Signatur, Schnittkandidaten, OM-Kacheln. Die Rechenlogik stammt aus `document_generator.py` und `src/seqcarto`. |
| `worker-text`, `worker-sequence`, `worker-music` | Celery 5, je eigenes schlankes Image | Libretto (TXT/MD), FASTA, MusicXML. Externe Inhalte werden mit begrenzten Ressourcen verarbeitet. |
| `db` | PostgreSQL 16 | Metadaten, Revisionen als JSONB |
| `queue` | Redis 7 | Broker und SSE-Pub/Sub |
| `storage` | MinIO (lokal) / S3 | Originale und Derivate, privat. Schnittstelle `Storage` mit Backends `local` und `s3`. |

Grundsätze:

- **Kernlogik ohne UI und Transport**: Positionsmodell, Hierarchie-Algorithmus, Platzierungsoperationen und Austauschformat liegen in einem reinen Python-Paket `core/`, das von API und Workern genutzt wird. Für die Vorschau im Client gibt es eine TypeScript-Entsprechung. Beide prüfen sich gegen **dieselben Testvektoren** in `spec/fixtures/`.
- **Geometrie** (Spirale, Weglängentabelle, Rückprojektion, Zeilenumbruch) ist ein eigenes TypeScript-Modul ohne Angular-Abhängigkeit und wird mit Vitest getestet.
- **Detailstufen**: Derivate sind adressiert (`[start, end)` in Sequenz- oder Quellkoordinaten) und werden in Stufen erzeugt. L0 ist eine Atlas-Signatur mit ca. 1–4 k Samples, L1 sind Segmentsignaturen für die große Rolle, L2 sind Detailkacheln wie OM-Kacheln, Basenfenster oder Taktgruppen. Der Client lädt nur, was sichtbar ist.
- **Revisionen**: Jede Schreiboperation nennt ihre Ausgangsrevision. Die API wendet sie atomar an und legt eine neue `SequenceRevision` an. Konflikte beantwortet sie mit `409` und liefert den aktuellen Stand mit. Rückgängig und Wiederholen erzeugen neue Revisionen.

## 3. Datenmodell und Übernahme aus Video Score

| Video Score | Sequence Cartography |
|---|---|
| `Movie` | `SourceAsset` (Profil `video`, Länge in ms, Prüfsumme, Herkunft) und `SourceDerivative` (Proxy, Frame-Zeitstempel-Tabelle, Stripes, OM-Kacheln, Signaturen) |
| `Tag` (`CUT`, Frame-Nummer) | `Suggestion` (Schnittkandidat) aus einem `AnalysisRun` mit Parametern und Versionen. Erst eine Bestätigung macht daraus einen `StructureTag`. |
| `Document` + `contentIndex` | `Sequence` + `SequenceRevision` |
| `ContentElement` `movieref {s, e}` | `Placement {assetId, sourceStart, sourceEnd}` in ms, halboffen: `sourceStart = pts(s)`, `sourceEnd = pts(e+1)` bzw. das Medienende beim letzten Frame. Wenn nur fps bekannt ist, wird die Genauigkeit als `fps-derived` gekennzeichnet. |
| `User` | `User`, `Project`, `ProjectMember` (Eigentümer, Bearbeiter, Leser) |

Die Übernahme läuft über einen versionierten Adapter `importers/video_score_v0`. Er liest einen Postgres-Dump (`frametag`, `movies`, `document`, `contentelement`) und erzeugt einen Importbericht mit fehlenden Quellen, ungültigen Verweisen und unsicheren Zeitgrenzen. Geprüft wird das mit einer kleinen selbst erzeugten Testquelle auf gleiche Reihenfolge, gleiche Grenzen und richtige Behandlung des letzten Frames.

## 4. Repository-Zielstruktur

```
client/              Angular-App (modernisiert)
api/                 Flask-API (aus server/ hervorgegangen), migrations/, tests/
workers/video/       Video-Worker (aus server/app/celerytasks + src/seqcarto)
workers/{text,sequence,music}/
core/                Python-Paket: Positionsmodell, Hierarchie, Platzierungen, Austauschformat
spec/schema/         JSON-Schema des Austauschformats
spec/fixtures/       gemeinsame Testvektoren (Python + TypeScript)
deploy/              compose.yaml (dev), compose.prod.yaml, gateway/nginx, .env.example
deploy/revival/      historischer Video-Score-Stack (M0)
docs/                Architektur, Spezifikation, Herkunft
legacy/              Prototyp 2018/19
```

`server/` und `client/` werden schrittweise umgezogen beziehungsweise modernisiert, damit die Git-Historie nachvollziehbar bleibt (`git mv` statt Neuanlage).

## 5. Meilensteine

| | Ziel | Abnahme |
|---|---|---|
| **M0** | Video Score läuft reproduzierbar in Containern (Revival) | Film anlegen, Stripes, Schnitte, Dokument und OM-Bilder im alten Client |
| **M1** | Neuer Stack-Rahmen auf dem Linux-Server: `deploy/compose.yaml` mit gateway, api, worker-video, db, queue, storage; Migrationen, Healthchecks, CI | `docker compose up` startet alles, Tests laufen in CI |
| **M2** | Durchgehender Videofall: Clip importieren → Schnitte → OM → Sequenz → dieselbe Stelle auf Kreiskarte, Leseseite und im Player | E2E-Test mit selbst erzeugtem Testclip |
| **M3** | Anmeldung, Projekte, Rollen, Atlas, Import Video und FASTA, persistente Karten | Abnahme 1, 2, 9 |
| **M4** | Gliederung (Tags, Hierarchie), Umbrüche, Revisionen, Undo, Konflikte | Abnahme 4, 6 |
| **M5** | Montage (Kopieren, Einfügen, neue Sequenz), Austauschformat | Abnahme 7, 11 |
| **M6** | Libretto, MusicXML, Mehrstimmigkeit | Abnahme 3, 8 |
| **M7** | Übernahme alter Video-Score-Dokumente, Performance, Demo-Atlas | Abnahme 5, 10 |

## 6. Offene Entscheidungen

1. **Linux-Server**: welcher Host (z. B. `tsv100`)? Hat er eine GPU, wie viel Speicher, wie ist er erreichbar (Reverse Proxy, Domain, TLS)?
2. **Identitätsdienst**: eigene Konten in der App oder ein vorhandener OIDC-Dienst (z. B. Keycloak)?
3. **Client**: das Angular-9-Projekt per `ng update` stufenweise hochziehen (9 → 20, viele Zwischenschritte) oder ein neues Angular-Projekt anlegen und die Komponenten übertragen. Empfehlung: neu anlegen und übertragen. Das alte Projekt bleibt bis M2 als Referenz lauffähig.
4. **API-Framework**: Flask beibehalten, wie der Bauauftrag verlangt. FastAPI wäre die Alternative.
5. **Demo-Material**: selbst erzeugte oder frei lizenzierte Videos, RNA, Libretto und Partitur. Die alten Testfilme (kommerzielle Spielfilme) dürfen nicht ins Repo und nicht in die Demo.

## 7. Erweiterungen, die die Architektur offenhalten muss

- **Online-Videos als Sequenz** (z. B. YouTube): als eigener **Connector** im Import (Abschnitt 5 des Bauauftrags), getrennt vom Video-Importer. Der Connector liefert eine Datei, danach läuft derselbe Video-Pfad. Wenn nur eine Referenz möglich ist, wird das als Status sichtbar gemacht.
- **Token-Sequenzen** (z. B. Tokenfolgen von Sprachmodellen): eigenes Profil mit ganzzahligem Token-Index als Koordinate. Zeichen sind die Token-Texte, dazu optionale Spuren (Logprobs, Attention-Werte, Rollen) als Features. Das gemeinsame Modell (Position, Platzierung, Tag, Feature) trägt das ohne Änderung. Nötig sind nur ein Importer und ein Renderer.
- Weitere Profile kommen nach demselben Muster dazu: Importer, Validierung, Adressformat, Renderer in mehreren Detailstufen.

## 8. Hintergrundverarbeitung

Empfehlung: **Celery 5** mit Redis, getrennte Queues je Worker-Image (`video`, `text`, `sequence`, `music`). Der Zustand eines Auftrags liegt in unserer eigenen Tabelle `AnalysisRun` (wartet, läuft, bereit, mit Hinweisen, fehlgeschlagen, abgebrochen) und nicht im Celery-Result-Backend. Fortschritt geht über Redis-Pub/Sub als SSE an den Client. So bleibt der Task-Runner austauschbar.

Alternativen, die geprüft wurden:

| Werkzeug | Eigenschaft | Bewertung |
|---|---|---|
| Celery 5 | Standard, Routing auf Queues, Abbruch, Flower | passt, schwergewichtige Konfiguration |
| Dramatiq | schlanker, zuverlässige Wiederholungen | gute Alternative |
| Procrastinate | Queue in PostgreSQL, Einreihen in derselben Transaktion wie die Revision | interessant für Idempotenz, ein Dienst weniger |
| arq, Taskiq | asyncio-basiert | eher für viele kurze I/O-Jobs, nicht für lange Videoanalysen |
| Temporal, Hatchet | dauerhafte Workflows | für den Anfang zu schwer |
