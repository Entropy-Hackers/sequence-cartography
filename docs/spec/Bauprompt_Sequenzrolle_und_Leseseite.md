# Sequence Cartography

## Bauauftrag für eine Webapp zum Kartieren, Lesen und Editieren langer Sequenzen

Baue eine neue, funktionsfähige Webapp namens **Sequence Cartography** im Repository [Entropy-Hackers/sequence-cartography](https://github.com/Entropy-Hackers/sequence-cartography). Das Produkt ist ein Atlas für lange, geordnete Sequenzen mit innerer Gliederung und darstellbarem Inhalt. Menschen öffnen ein Projekt, sehen darin zuerst die kreisförmigen Karten ihrer Sequenzen, tauchen in eine davon ein, erkennen Abschnitte, lesen Details und arbeiten mit dem Material weiter.

Eine RNA, ein Video, ein Opernlibretto und eine Musikpartitur müssen als gleichwertige Karten nebeneinander liegen können. Eine RNA zeigt Basen und markierte Bereiche. Ein Film zeigt Bilder und Ton. Ein Libretto zeigt Text, Rollen und Einsätze. Eine Musikpartitur zeigt Form, Takte, Motive und gleichzeitig verlaufende Stimmen. Jede Karte hat dieselbe grundlegende Geometrie und dieselben Interaktionen. Ihre Maßeinheit, ihre visuellen Zeichen und ihre Gliederung kommen aus dem jeweiligen Material.

Die Gliederung kommt von Marken **in der Sequenz**. Eine Marke hat einen Rang wie eine Überschrift in einem Buch. `H1` kann im Opernprojekt **Akt** heißen, `H2` **Schauplatz oder Kapitel**, `H3` **Szene** und `H4` **Musiknummer oder Lied**. Andere Projekte können dieselben Ränge anders benennen. Die Inhalte bleiben entlang der Folge lesbar. Von Anfang bis Ende gibt es eine gemeinsame Reihenfolge der Positionen. An einer Position können mehrere Inhalte gleichzeitig liegen, etwa die Einsätze mehrerer Stimmen in einer Partitur. Die Fläche entsteht, indem die Spur aufgerollt oder wie Text umgebrochen wird.

## 0. Codebasis und Zielrepository

Entwickle **Sequence Cartography** aus dem Code von [human-centered-ai-lab/app-video-score](https://github.com/human-centered-ai-lab/app-video-score) weiter. Das Produktrepository ist [Entropy-Hackers/sequence-cartography](https://github.com/Entropy-Hackers/sequence-cartography). Der dort unter `legacy/` archivierte frühe Prototyp bleibt als historisches Material erhalten. Für die technische Weiterentwicklung dient **Video Score** als Ausgangspunkt. Die Benutzeroberfläche von Sequence Cartography erhält den in diesem Bauauftrag beschriebenen Atlas und Editor.

Prüfe zu Beginn den aktuellen Stand beider Repositories und die vorhandenen Projektvorgaben. Für diesen Bauauftrag wurde Video Score auf `master` bei Commit `6383f18164a96c64a80de15ebba00b4559842ce4` eingesehen. Halte den tatsächlich übernommenen Commit und die Herkunft des Codes im Zielrepository fest. Wenn die Codebasis dort noch fehlt, integriere sie auf einem Arbeitszweig über einen Upstream-Remote mit nachvollziehbarer Git-Herkunft. Bewahre vorhandene Arbeit und die Lizenz- und Copyright-Hinweise für übernommenen Code. Wenn die Integration bereits erfolgt ist, arbeite auf dem vorhandenen Stand weiter.

### Konkrete Übernahme

| Vorhandener Code in Video Score | Weiterentwicklung in Sequence Cartography |
| --- | --- |
| `client/` mit Angular und NgRx | Bestehenden Client schrittweise modernisieren. Wiederverwendbare Video- und Vorschaukomponenten in den neuen Editor integrieren. Projektatlas, Kreiskarte, Leseseite und Projektverwaltung als neue Oberflächen in dieser Anwendung entwickeln. |
| `server/app/celerytasks/tasks.py` mit Videoanalyse, Schnittsuche, Slit-Scan und Statusmeldungen | Vorhandene Videoverarbeitung in den Video-Importer und die Analyseaufträge überführen. Rechenlogik und Task-Ablauf als Grundlage weiterverwenden. Ergebnisse an Quelle, Analyseversion und Projekt binden. |
| `server/app/celerytasks/document_generator.py` und `client/src/app/document/document-display/omimage/` | OM-Bilder weiter erzeugen und in der Leseseite anzeigen. Die bestehende Auswahl einer Bildstelle an die gemeinsame Positionsabbildung koppeln. Vorschauen über projektspezifisch autorisierte Derivate laden. |
| `server/app/models/` mit `Movie`, `Document`, `ContentElement` und Frame-Tags | Bestehende Konzepte auf `SourceAsset`, `Sequence` und `Placement` abbilden. Videodaten als erstes Profil des gemeinsamen Modells übernehmen. |
| Flask-API, PostgreSQL, Celery, Redis und Compose | Die vorhandene Aufteilung als Ausgangspunkt für API, Persistenz, Hintergrundverarbeitung und reproduzierbaren lokalen Betrieb verwenden. Abhängigkeiten, Laufzeit und Startkonfiguration aktualisieren. |

Die erste durchgehende Übernahme ist ein realer Videofall. Importiere einen kurzen Clip, ermittle Schnitte und erzeuge daraus ein OM-Bild. Überführe das Ergebnis in eine neue Sequenz und öffne dieselbe Stelle auf der Kreiskarte, in der Leseseite und im Player. Verifiziere diesen Pfad mit einer reproduzierbaren Testquelle. Die analytische Logik und die OM-Darstellung stammen aus Video Score und werden an das neue Modell angepasst. RNA, DNA, Libretto und Partitur erhalten ihre eigenen Importer und Renderer auf dieser gemeinsamen Grundlage.

### Bestehende Videodokumente und Koordinaten

Lies bestehende Dokumente über einen versionierten Adapter oder eine explizite Migration. Ein historisches `Document.contentIndex` enthält die Reihenfolge der Elemente. Ein `movieref`-Element verweist über `movieuuid` auf das Quellvideo und gibt den Ausschnitt über die beiden Framegrenzen `s` und `e` an. Der vorhandene Generator behandelt `e` als eingeschlossen. Überführe solche Bereiche in halboffene Intervalle vom Zeitstempel des ersten Frames bis zum Zeitstempel nach dem letzten Frame. Für den letzten Frame nutze das ermittelte Medienende. Verwende die tatsächlichen Frame-Zeitstempel, wenn sie verfügbar sind. Kennzeichne die Genauigkeit, wenn bei einem dokumentierten Material mit konstanter Framerate nur die Framezahl und Framerate vorliegen. Melde fehlende Quellen, ungültige Verweise oder nicht zuverlässig auflösbare Zeitgrenzen im Importbericht.

Filmbezogene Frame-Tags werden zunächst Schnittkandidaten oder Quellmerkmale. Eine bestätigte dramaturgische Gliederung wird ausdrücklich zu Sequenz-Tags. Alte Cache-Pfade, feste Bildbreiten und Laufzeitannahmen werden bei der Übernahme von der neuen Darstellung getrennt. Nutze eine lokale Testquelle, um gleiche Reihenfolge und Ausschnittgrenzen sowie die Behandlung des letzten Frames zu prüfen.

Übernimm die vorhandenen Demo-Benutzerrouten und direkten Medienpfade nur nach Umstellung auf die projektgebundenen Zugriffsregeln aus Abschnitt 2. Entkopple den Video-Importer von historischen Anbieterbibliotheken und statischen lokalen Pfaden. Aktuelle, unterstützte Eingänge gehen durch die gemeinsame Importprüfung aus Abschnitt 5.

## 1. Die Erfahrung beim Öffnen eines Projekts

1. Ich melde mich an. Gibt es ein zuletzt geöffnetes Projekt, das ich weiterhin sehen darf, öffnet sich dessen **Atlas**. Andernfalls komme ich zur Projektauswahl. Bei einem neuen Konto kann ich ein Projekt anlegen oder eine vorbereitete Demo öffnen.
2. Im Atlas sehe ich zuerst die **Kreiskarten**. Jede Karte steht für eine ganze Sequenz. Auf der Karte erkenne ich Form, Umfang und auffällige Gliederung auf einen Blick. Titel, Materialtyp und Länge stehen bei der Karte. Daneben oder darüber finde ich kompakt den Projektwechsel und den Import.
3. Ich kann schon in der Übersicht auf eine sichtbare Stelle einer Karte zeigen. Bei ausreichender Kartengröße sehe ich eine Adresse und den Abschnittsnamen. Ein Klick auf die Karte öffnet die große Karte im Editor. Ein Klick auf eine genaue Stelle übernimmt diese Position. Titel und Tastaturaktion öffnen dieselbe Karte.
4. Im Editor sehe ich die ganze Spur. Ich wähle eine Position, eine Szene, ein Kapitel oder einen freien Bereich. Inhaltsverzeichnis, Materialansicht und Karte beziehen sich auf dieselbe Auswahl.
5. Ich entrolle den gewählten Bereich zu einer ganzen Leseseite. Wie in einem Buch erkenne ich Kapitel, Szenen und ihren Zeilenfluss. Ich kann den Inhalt direkt entlang der Zeilen lesen, hören oder ansehen.
6. Ich kopiere eine sichtbare Zeile, einen beliebigen Bereich oder einen ganzen Abschnitt, wechsle innerhalb des Projekts zu einer anderen Sequenz und füge die Auswahl an einer gewählten Position ein. Ich kann aus der Auswahl auch eine neue Sequenz anlegen. Danach erscheint ihre eigene Kreiskarte im Atlas.
7. Ich kehre zum Atlas zurück und finde meine Sammlung und ihren Stand wieder. Wenn ich denselben Editor erneut öffne, kann ich an meiner letzten Stelle weiterarbeiten.

### Bildreferenz für die Kreiskarte

Verwende die mitgegebene RNA-Karte als visuelle Referenz. Kennzeichnend sind der helle Grund, ein klarer Titel mit knapper Metazeile, die vielen eng beieinanderliegenden Windungen einer einzigen Spur, farbige Abschnitte und vereinzelte dunkle Grenzpunkte. Ein größerer Ring hebt die aktive Stelle hervor. Man kann auf der Karte sehen, wo die Spur in der Mitte beginnt und wo sie außen endet. Die Komposition soll auch für einen Film oder ein Libretto funktionieren. Die Referenz bestimmt die visuelle Sprache. Ihre Farben und Abschnittsgrenzen sind Bildbeispiele.

Der Atlas besteht aus einem ruhigen Raster ausreichend großer, eigenständiger Karten. Video, RNA, Text und Musikpartitur bleiben an ihrem Zeichenmaterial erkennbar. Biete Suche nach Titeln und Filter nach Typ und Status in einer kompakten Leiste. Beim Erstellen oder Importieren erscheint die neue Karte mit einem nachvollziehbaren Status. Eine fertige Karte und eine aktuell bearbeitete Karte stehen im selben Raster. Die Übersicht bleibt beim Zurückkehren an ihrer früheren Scrollposition.

## 2. Produktaufbau und Navigation

| Bereich | Aufgabe und sichtbarer Inhalt |
| --- | --- |
| Anmeldung und Konto | Konto anlegen, anmelden, abmelden, Passwort zurücksetzen oder vorhandenen Identitätsdienst verwenden, Profil verwalten |
| Projektauswahl | Eigene und freigegebene Projekte, zuletzt geöffnet, neues Projekt, archivierte Projekte |
| Projekt · Atlas | Startseite des Projekts mit Kreiskarten, Suche, Filtern, Import und neuer leerer Sequenz |
| Projekt · Material | Quellen mit Herkunft, Typ, Länge, Verarbeitungsstand, Vorschau und Verwendung in Sequenzen |
| Projekt · Analysen | Laufende und abgeschlossene Aufträge, Fortschritt, Hinweise, Fehler und Vorschläge |
| Projekt · Einstellungen | Projektname, Mitglieder und Rollen, Hierarchieprofile, Standarddarstellung, Archivierung |
| Sequenzeditor | Große Rolle und Leseseite, Inhaltsverzeichnis, Materialansicht, Struktur- und Bereichsbearbeitung, Versionsstand |

Projekte sind private Arbeitsräume mit dauerhaftem Zustand. Ein Projekt hat mehrere Quellen und mehrere Sequenzen. Eine Quelle kann in mehreren Sequenzen vorkommen. Eine Sequenz kann aus mehreren Quellen desselben Typs und derselben kompatiblen Koordinate bestehen. Ein Projekt kann Karten mehrerer Typen und mehrere Hierarchieprofile enthalten. Ein Projekt zur Oper kann etwa das Libretto in Wörtern und zwei unterschiedliche Videoaufnahmen in Millisekunden nebeneinander zeigen.

Unterstütze die Rollen **Eigentümer**, **Bearbeiter** und **Leser**. Eigentümer verwalten Projekt, Mitglieder, Rollen und Archivierung. Bearbeiter importieren und analysieren Material, ändern Sequenzen und bearbeiten Gliederungen. Leser öffnen Karten, Seiten, Material und freigegebene Versionen. Erlaube eine Einladung per adressierter Einladung mit Ablaufdatum oder über den Identitätsdienst der vorhandenen Infrastruktur. Prüfe Berechtigungen im Server für jeden Zugriff auf Projekt, Sequenzen, Revisionen, Analyseergebnisse, Vorschaubilder, Originale und Exporte. Sichere auch die Freigabe von Streaming- und Download-URLs. Zeige in der Oberfläche die Aktionen passend zur Rolle. Archivierte Projekte lassen sich durch Eigentümer wieder öffnen.

Der Editor erhält eine stabile URL mit Projekt und Sequenz. Verwende bei Bedarf einen Positions- oder Abschnittsparameter, der zusammen mit der passenden Revision eindeutig interpretierbar ist. Direkte Links durchlaufen dieselbe Zugriffskontrolle. Die Toolbar stellt Titel, Einheit, Länge, ausgewählte Position, **Rolle / Leseseite**, Rückgängig, Wiederholen und Speicherstatus gut sichtbar bereit. Ein- und ausklappbares Inhaltsverzeichnis und Inspektor lassen der Karte ausreichend Raum. Auf einem schmalen Display werden sie zu aufrufbaren Paneelen. Die zentrale Fläche bleibt Karte oder Leseseite.

## 3. Das gemeinsame Sequenzmodell

### Ordnung, Inhalt und Gliederung

Eine Sequenz ist ein endlicher geordneter Bereich `[0, Länge)` mit einer definierten Maßeinheit und einem Inhaltsprofil. Die Position ist eine Adresse auf der Folge. Für eine Videoaufnahme kann sie die Wiedergabezeit sein. Für RNA ist sie ein Basenindex. Für ein Libretto ist sie zum Beispiel ein Wortindex. Für eine Musikpartitur ist sie eine notierte musikalische Position, darstellbar als Takt, Zählzeit und Unterteilung. Ein Profil legt fest, welche Zeichen dargestellt werden, wie Adressen angezeigt werden und welche Auswahlgrenzen zulässig sind. Eine Karte muss auch dann funktionieren, wenn es keine Uhr und keine Wiedergabezeit gibt.

| Profil | Interne Koordinate | Material auf der Karte und in der Leseseite | Mögliche Struktur |
| --- | --- | --- | --- |
| Video | Ganzzahlige Millisekunden | Farbsignatur und Schnittmarken in der Übersicht, Keyframes, Miniaturen, Slit-Scan und bei Bedarf Audio im Detail | Akt, Kapitel, Szene, Einstellung |
| RNA und DNA | Nullbasierte Position in der importierten Basenfolge | Aggregierte Basensignatur in der Übersicht, Basenbuchstaben und optionale Merkmale in der Nahsicht | Projektdefinierte Bereiche und Unterbereiche aus einer expliziten Gliederung |
| Libretto | Index in einer beim Import festgelegten Wortfolge | Textfluss, Rollen, Regieanweisungen, Refrains und Wortlaut mit Satzzeichen | Akt, Schauplatz, Szene, Musiknummer, Unterabschnitt |
| Musikpartitur | Ganzzahlige Ticks auf einer musikalischen Achse mit Taktkarte | Abschnitte, Dichte und Stimmen in der Übersicht, Takte, Noten, Pausen, Motive und vertikal ausgerichtete Stimmen im Detail | Werkteil, Satz, Formabschnitt, Phrase |
| Weitere Profile | Diskrete, geordnete Adressen oder definierte ganzzahlige Ticks | Profilabhängige Zeichen, Bilder, Text oder Werte | Projektdefinierte Hierarchie |

Interne Intervalle sind halboffen. Die Profile übernehmen die verständliche Anzeige. Bei RNA kann das erste Zeichen intern Index `0` haben und als Base `1` angezeigt werden. Speichere Importformat und Koordinatenkonvention ausdrücklich. Wandlungen aus einer einbasierten inklusiven Quelle müssen Anfang und Ende korrekt abbilden. Für Text speichere zusätzlich die Zuordnung von Wortgrenzen zu Originaltext. Der detailgenaue Ausschnitt behält Satzzeichen, relevante Zeilenumbrüche und Sprecherangaben. Definiere und versioniere die Tokenisierung. Für Video sollen Player und Inspektor bei Bedarf tatsächliche Frame-Zeitstempel zum Einrasten anbieten. Die Speicherung bleibt in Millisekunden.

Jedes unterstützte Profil hat Funktionen zum Importieren, Validieren, Angeben der Länge, Formatieren von Adressen, Laden von Materialausschnitten und Bereitstellen von visuellen Daten in mehreren Detailstufen. Die Geometrie, der Hierarchiealgorithmus und die Schnittoperationen verwenden nur das gemeinsame Positionsmodell. Neue Profile sollen über diese Schnittstelle hinzukommen. Die externe Umwandlung in Video ist ein möglicher zusätzlicher Eingang für bisher ununterstützte Daten. Ihre Originaladressen können als Zuordnung mitgegeben werden.

### Entitäten und Zuordnungen

| Entität | Verantwortung |
| --- | --- |
| `User`, `Project`, `ProjectMember` | Identität, Arbeitsraum, Rollen und persönliche Einstellungen |
| `SourceAsset` | Unveränderliche importierte Quelle mit Original, Profil, Länge, Herkunft, Prüfsumme und gegebenenfalls Referenz-URL |
| `SourceDerivative` | Adressierbare abgeleitete Vorschauen, Proxies, Bilder, Wellenformen oder Aggregatdaten |
| `AnalysisRun`, `Suggestion` | Zustand, Herkunft, Parameter, Kandidaten, Bezug zur Quelle oder zu einer konkreten Revision |
| `Sequence` | Titel, Projekt, Inhaltsprofil, verwendetes Hierarchieprofil und aktuelle Revision |
| `SequenceRevision` | Konsistenter, versionierter Stand von Materialbelegung, Tags und weiteren projektbezogenen Merkmalen |
| `Placement` | Verwendung eines bestimmten Ausschnitts einer Quelle an einer Position in der Sequenz |
| `StructureTag` | Startmarke mit stabiler ID, Position, Hierarchieebene, Titel und Herkunft |
| `Feature` | Position oder Intervall mit Typ, Eigenschaften, Herkunft und Bindung an Quelle oder Sequenz |

Trenne die Adresse in der **Quelle** von der Adresse in der **bearbeiteten Sequenz**. Eine Sequenz speichert eine geordnete Liste von Platzierungen mit `assetId`, `sourceStart` und `sourceEnd`. Die Position einer Platzierung in der Sequenz ergibt sich aus den Längen der vorhergehenden Platzierungen. Der erste Import einer vollständigen Quelle verwendet eine Platzierung von ihrem Anfang bis zu ihrem Ende. Bei einer bearbeiteten Sequenz kann dieselbe Quelle mehrfach an verschiedenen Stellen auftreten. Suche nach einer Quellstelle gibt dann jede passende Verwendung zurück. Ein Sprung aus einer Auswahl zum Quellmaterial verwendet die konkret ausgewählte Platzierung.

Verwende in der ersten Version durchgehende, aneinander anschließende Platzierungen auf einer einzigen Ordnungsachse. In einer Platzierung können mehrere Stimmen, Spuren und überlappende Ereignisse auf derselben Achse liegen. Jede Platzierung hat positive Länge und gültige Grenzen in einer zugänglichen Quelle. Änderungen am Aufbau entstehen durch Bearbeiten der Platzierungen. Für RNA-Assemblagen gilt die gespeicherte Leserichtung. Eine fachliche Operation wie das Rückwärtskomplement wäre ein eigener, ausdrücklich benannter Verarbeitungsschritt. Kompatible Quellprofile teilen eine Maßeinheit und die für die Darstellung nötige Semantik. Inkompatible Profile werden bei der Einfügeprüfung mit Typ und Einheit ausgewiesen.

### Austauschformat

Dokumentiere ein versioniertes JSON-Format für Sequenzen mit Tags, gesetzten Layoutmarken, Sequenzmerkmalen und profilabhängigen Daten zur Achse und zu parallelen Spuren. Quellgebundene Inhalte bleiben über das Quellenmanifest wiederherstellbar. Liefere ein Schema oder einen ausführbaren Validator und mindestens eine Beispieldatei je Startprofil. Exportiere Projektinhalte nach Nutzeraktion in portabler Form mit Quellenmanifest, stabilen Schlüsseln und optionalen Quelldateien. Der Import muss Medien vor dem Auflösen der Referenzen zuordnen können. Zeige fehlende Quellen und biete ihre Zuordnung an. Eine kleinere Tag-Datei soll sich separat importieren und exportieren lassen, mit explizitem Bezug auf die Koordinate der ausgewählten Sequenz. Quelldaten und geheime Zugriffsinformationen haben getrennte Felder. Das Austauschformat enthält keine Zugangsdaten oder ablaufenden Download-URLs.

Beispiel für eine RNA-Sequenz aus einer bereits zugeordneten Quelle mit mindestens 36 Basen. Die Marken sind frei erfundene Demo-Struktur.

```json
{
  "schemaVersion": 1,
  "title": "RNA-Demo · Ausschnitt",
  "profile": "rna",
  "coordinate": { "unit": "base", "origin": 0, "end": "exclusive" },
  "sources": [{ "key": "rna-demo", "length": 36 }],
  "placements": [
    { "id": "p1", "source": "rna-demo", "sourceStart": 4, "sourceEnd": 16 },
    { "id": "p2", "source": "rna-demo", "sourceStart": 24, "sourceEnd": 36 }
  ],
  "levelLabels": { "1": "Teil", "2": "Abschnitt", "3": "Passage" },
  "tags": [
    { "id": "t1", "at": 0, "level": 1, "title": "Teil A" },
    { "id": "t2", "at": 0, "level": 2, "title": "Erster Ausschnitt" },
    { "id": "t3", "at": 12, "level": 2, "title": "Zweiter Ausschnitt" }
  ]
}
```

Die Gesamtlänge ist 24. Sequenzposition `12` beginnt im zweiten Ausschnitt an Quellposition `24`. Der erste Abschnitt belegt `[0,12)`, der zweite `[12,24)`. Nach dem Export und Wiederimport liefern beide Ansichten dieselbe Zuordnung. Vereinheitliche Feldnamen über Import, Export und API oder dokumentiere die Abbildung eindeutig.

## 4. Wie die Hierarchie entsteht

Die Struktur einer Karte wird aus ihren `H1`-, `H2`-, `H3`- und weiteren Tags berechnet. `H1` ist die höchste Ebene. Projektprofile bestimmen Namen, Zeichen und Zuordnung zu Seite und Absatz. Ebenennummern sind positive Ganzzahlen. Ein Abschnitt hat genau die Grenzen, die der Tag-Algorithmus aus der Sequenz ableitet.

1. Sortiere Tags nach Position und bei gleicher Position von der gröbsten zur feinsten Ebene.
2. Eine Marke der Ebene `k` schließt alle offenen Abschnitte der Ebene `k` und tiefer an dieser Position. Sie eröffnet ihren eigenen Abschnitt unter dem nächstgelegenen noch offenen übergeordneten Abschnitt oder direkt an der Wurzel.
3. Eine feinere Marke lässt ihren übergeordneten Abschnitt weiterlaufen. Ein Akt, ein Kapitel und eine Szene können an derselben Position beginnen.
4. Die letzten Abschnitte enden am Sequenzende. Lasse übersprungene Ebenen und sichtbare unbeschriftete Vorläufe zu. Weise bei Bedarf neutral darauf hin.
5. Akzeptiere Anfangsmarken ab Position null und vor dem Sequenzende. An einer Position gibt es pro Ebene eine Startmarke. Melde doppelte IDs, Konflikte und ungültige Werte im Import mit der betroffenen Stelle. Die Rolle, die Leseseite und das Inhaltsverzeichnis leiten ihre Abschnitte aus demselben Ergebnis ab.

Ein Vorhang, eine Pause, ein Ort- oder Rollenwechsel können als Hinweise im Material auftauchen. Beim Libretto können explizite Überschriften unmittelbar für die Struktur verwendet werden. Ein automatischer Fund bleibt ein Vorschlag, solange seine Hierarchie unklar ist. Ein Sprecherwechsel kann beispielsweise ein Merkmal innerhalb einer Szene sein. Ein Filmschnitt kann eine neue Einstellung markieren. Die Begriffe Akt, Kapitel oder Szene stammen aus der konkreten Gliederung oder werden durch einen Menschen vergeben.

Einige Materialien enthalten zusätzliche, auch überlappende Merkmale. Dazu gehören annotierte RNA-Intervalle, wiederkehrende Motive, Tonereignisse oder Rollenauftritte. Speichere solche Merkmale getrennt von der Gliederung und stelle sie auf der Spur als optionale Markierungen dar. Bei einer RNA können Merkmale auf derselben Folge überlappen. Die Projektgliederung kann parallel eigene Kapitel oder Analyseabschnitte haben. Ermögliche eine ausdrückliche Übernahme eines geeigneten Merkmals als Startmarke. Zeige dabei, welche bestehenden Abschnitte die neue Marke öffnet oder schließt.

Jede Marke lässt sich am aktuellen Cursor setzen, umbenennen, verschieben, umstufen und löschen. Der Inspektor zeigt ihren Ursprung, ihre native Position und den betroffenen Bereich. Zeige an einer gemeinsamen Position alle Ebenen. Unterstütze das Prüfen von Analysevorschlägen einzeln oder nach Filter in Gruppen. Eine neue Analyse erzeugt neue Vorschläge und lässt bestätigte Bearbeitungen bestehen.

## 5. Import und Verarbeitung

Biete eine sichtbare Importaktion im Atlas und einen vollständigen Importdialog mit Profil, Quelle, Titel, Hierarchieprofil und optionaler Tag-Datei. Unterstütze **Datei hochladen** und **Link einfügen**. Erkläre vor dem Start, welchen Inhalt die App für den Link abrufen und verarbeiten kann. Zeige bei URL-Import Domain, erkannten Typ und Dateigröße, soweit verfügbar. Unterscheide abrufbare Dateien von Seiten- oder Anbieterlinks. Eine freigegebene Direkt-URL und ein Upload müssen für unterstützte Formate tatsächlich funktionieren. Für einen Anbieterlink kann ein separater unterstützter Connector Inhalt liefern. Wenn nur eine externe Referenz gespeichert werden kann, zeige diesen Status und biete die Zuordnung einer hochgeladenen Datei an.

### Startprofile und ihre Verarbeitung

| Profil | Mindesteingänge | Ergebnis und Analyse |
| --- | --- | --- |
| Video | Unterstützte lokale Videodatei und abrufbare direkte Video-URL | Dauer und technische Metadaten, abspielbare Quelle oder Proxy, Farbsignatur, Vorschauen und automatisch gefundene Schnittkandidaten. Eingebettete Kapitel oder mitgelieferte Tags übernehmen, wenn ihre Koordinaten gültig sind. |
| RNA und DNA | FASTA-Datei, abrufbare FASTA-URL oder eingefügte FASTA-Sequenz | Validierte Basenfolge mit stabilen Indizes, Titel und Länge, aggregierte Basenverteilung und Detailansicht mit Symbolen. Optionale Intervallannotation mit expliziter Koordinatenkonvention. |
| Libretto | TXT oder Markdown als Datei oder abrufbare direkte URL | Originaltext, stabile Wortadressen, erhaltener Textfluss, Rollen und Regieanweisungen soweit strukturiert erkennbar. Markdown-Überschriften und eindeutige Akt- oder Szenenmarken sind importierbare Struktur beziehungsweise überprüfbare Vorschläge. |
| Musikpartitur | MusicXML als Datei oder abrufbare direkte URL | Eine gemeinsame notierte Achse, Taktkarte, Stimmen und Notenereignisse mit Einsatz und Dauer, gemeinsame visuelle Darstellung paralleler Stimmen. Lies Probenzeichen und vorgegebene Abschnittsmarken als mögliche Strukturkandidaten. |

Implementiere einen echten Verarbeitungsweg. Für Video analysiert ein Worker die Datei mit FFmpeg und ffprobe oder einem gleichwertigen Werkzeug. Er ermittelt Video-Zeitstempel, erzeugt Vorschauen und berechnet Schnittkandidaten anhand der tatsächlichen Bilder. Für RNA und DNA verarbeitet der Importer die Datei recordweise. Biete bei mehreren Records die Auswahl einzelner Records oder die Anlage je einer Karte an. Erhalte IUPAC-Mehrdeutigkeitszeichen und melde ungültige Zeichen nachvollziehbar. Der Importdialog lässt RNA und DNA ausdrücklich wählen und zeigt das jeweilige Alphabet. Eine gewünschte Umwandlung zwischen `T` und `U` ist sichtbar und erfolgt nur nach Auswahl. Für Libretti erfasst ein Importer Überschriften und den Originaltext einschließlich Anweisungen. Bei MusicXML müssen Akkorde, Pausen, überlappende Dauern und die notierte Reihenfolge erhalten bleiben. Leite eine gemeinsame Tickauflösung aus den notierten Unterteilungen ab. Halte Triolen und andere unterstützte rhythmische Unterteilungen exakt. Bei der Montage unterschiedlicher Auflösungen rechne auf ein gemeinsames Raster um und weise Fälle aus, die sich darin nicht exakt abbilden lassen. Unterscheide notierte Position und Aufführungszeit. Wiederholungszeichen bleiben sichtbar. Eine ausgeschriebene Aufführungsfolge kann später als eigener Importmodus hinzukommen. Übernimm explizite semantische Tags aus der zugehörigen Tag-Datei nach Validierung. Biete bei mehrdeutigen Markern die Vorschau an.

Nach erfolgreichem Import erstellt die App aus der Quelle eine erste gespeicherte Sequenz im gemeinsamen Format und zeigt sie im Atlas. Sobald die Quelle valide ist und die erste Sequenz steht, kann ich die Karte bereits öffnen. Abgeleitete Materialbilder und weitere Vorschläge erscheinen, sobald sie vorliegen. Kann der Analyzer wenig Struktur ableiten, ist die Quelle als ganze Spur lesbar und manuell gliederbar. Wenn ein späterer Analyseauftrag fehlschlägt, bleibt der bisherige nutzbare Sequenzstand erreichbar.

Zeige die Zustände **wartet**, **läuft**, **bereit**, **mit Hinweisen**, **fehlgeschlagen** und **abgebrochen** mit den für den Nutzer relevanten Details. Erneute Ausführung muss idempotent sein. Ein wiederholter Versuch darf keine zweite erste Sequenz oder doppelte Vorschläge erzeugen. Halte unterschiedliche Analyseparameter und Versionen nachvollziehbar. Setze Uploadgrenzen, Downloads mit Zeit- und Größenlimit sowie URL-Prüfung einschließlich Weiterleitungen und privater Netzadressen um. Prüfe Inhalt und Format serverseitig. Verarbeite Medien und Text aus externen Quellen in getrennten, begrenzten Prozessen oder entsprechend abgesicherter Infrastruktur. Stelle den Text sicher dar und speichere Quellen privat. Erlaube das erneute Zuordnen einer fehlenden Datei anhand ihres Manifests und nach Möglichkeit ihrer Prüfsumme.

## 6. Zeichenmaterial, Parallelität und visuelle Vergrößerung

Für jede Modalität muss es etwas geben, das der Nutzer tatsächlich im Editor lesen und auswählen kann. Implementiere eine gemeinsame Darstellungsschnittstelle mit getrennten Renderern für Übersicht, Bereich und Detail. Jeder Renderer gibt adressierte Elemente oder Aggregate zurück. Jeder sichtbare Baustein führt auf seine Position oder sein Intervall zurück. Der Nutzer kann aus einer abstrakten Signatur in genau die Zeichen oder Ereignisse hineinzoomen, aus denen sie entstanden ist.

| Material | Im Projektatlas | Beim Eintauchen | Auf der Leseseite und im Inspektor |
| --- | --- | --- | --- |
| Video und Ton | Farbsignatur der Bilder, grobe Kapitel, optionale Tonaktivität | Markante Bilder, Schnittgrenzen, Tonverlauf | Adressierte OM-Streifen und abspielbare Ausschnitte mit genauer Position |
| RNA oder DNA | Große Bereiche, markante Muster und relevante Annotationen | Wählbare Motive, Merkmalsintervalle, Zusammenfassungen von Basenfenstern, bei gegebener Lesart auch Codons | Abschnittsbezeichnungen und Merkmalsdetails, beim stärksten Zoom exakte Basen mit Koordinaten |
| Libretto und strukturierter Text | Akte, Kapitel, Szenen und gegebenenfalls wiederkehrende Sprecher oder Textmotive | Rollen, Regieanweisungen, markante Textstellen | Lesbarer Wortlaut in seiner ursprünglichen Reihenfolge, auswählbare Wörter und Passagen |
| Musikpartitur | Formteile, Dichte, Einsätze und Signaturen ausgewählter Stimmen | Takte, Phrasen, Motive und gestaffelte Stimmen | Notationssysteme oder eine klar beschriftete Notenansicht mit ausgerichteten Stimmen, Einsatz, Dauer, Tonhöhe und Pause |

Das **OM-Prinzip** ist eine Möglichkeit, einen langen Bereich gleichzeitig in grober und feiner Auflösung zu zeigen. Die grobe Signatur lässt den Verlauf überblicken. Adressierte Stichproben und Details machen ihn lesbar. Für Video ist das historische OM-Bild mit großen Keyframes, kleinen Bildern und Slit-Scan der mittleren Bildspalte ein konkretes Vorbild. Baue es als adressierbaren Videorenderer, der in die Leseseite passt und bei Bedarf in Stücken lädt. Für andere Modalitäten entwirf ihre eigenen sinnvollen Darstellungen nach demselben Prinzip. Eine RNA kann als Folge von annotierten Bereichen und Motiven lesbar sein. Eine Partitur kann zuerst als Folge von Formteilen und Stimmenwechseln lesbar sein. Basen und Noten bilden die Feinauflösung.

Lasse je Karte umschalten, welche Signatur in der Übersicht und welche Merkmale im Detail sichtbar sind. In einer biologischen Karte stammen höhere Bedeutungen aus mitgegebenen Annotationen, aus einem ausdrücklich konfigurierten Algorithmus oder von der Nutzerin. Zeige Herkunft und Geltungsbereich. Bei Codons muss der verwendete Rahmen bekannt und angezeigt sein. Die App soll auch mit einer Basenfolge ohne solche Angaben arbeiten.

### Gleichzeitige Ereignisse

Trenne die **Ordnungsachse** von **Ereignissen und Spuren auf dieser Achse**. Ein Ereignis kann an einer Position beginnen, über ein Intervall dauern oder punktförmig sein. Es kann einer Stimme zugeordnet sein und Eigenschaften wie Tonhöhe, Notation, Rolle oder Farbe tragen. Mehrere Ereignisse können am selben Punkt starten und gleichzeitig andauern. Für eine Note speichere mindestens Stimme, Beginn, Dauer und Tonhöhe oder Pausentyp. Akkorde, Mehrstimmigkeit und gehaltene Noten werden in der richtigen zeitlichen Beziehung dargestellt. Ein Modell, das gleichzeitige Noten künstlich hintereinander schreibt, verfälscht die Partitur.

Die Spiralform bleibt eine gemeinsame Spur. Einzelne Stimmen können als feinere Begleitzeichen oder über eine gewählte Signatur dargestellt werden. In der entrollten Zeile liegen die Stimmen untereinander und verwenden dieselbe horizontale Positionsskala. Der vertikale Aufbau zeigt Gleichzeitigkeit. Die nächste Buchzeile setzt die Reihenfolge fort. Technische Zeilenumbrüche für Musik liegen bevorzugt an Taktgrenzen. Die Leseansicht darf musikalischen Platz für lesbare Notation verteilen, solange dieselbe Position in allen sichtbaren Stimmen übereinander liegt und alle Treffer genau auf die Achse zurückführen. Biete für die vergleichende Übersicht eine feste Maßstabseinstellung mit proportionalen Längen. Tempo und optionale Aufnahme gehören zu einer gesonderten Zeitabbildung.

Das gleiche Prinzip erlaubt Videobild und Ton sowie überlappende RNA-Annotationen auf einer gemeinsamen Achse. Weitere Modalitäten sollen eigene Spuren anbieten können. Die App muss eine gemeinsame Achse aus den Importdaten oder einer expliziten Zuordnung kennen, bevor sie Spuren aus verschiedenen Quellen synchron anzeigt. Mehrere unabhängige Karten können ohne solche Zuordnung im selben Projekt liegen.

## 7. Die Spiralrolle und der Weg in die Leseseite

### Die Rolle

Zeichne eine einzige kontinuierliche Spirale mit ihrem Anfang in der Mitte und ihrem Ende außen. Eine lange Sequenz soll in einer großen Kartenansicht typischerweise etwa **20 bis 40 sichtbare Windungen** haben. Wähle den Abstand so, dass die Spur über die gesamte Fläche hinweg erkennbar ist. Passe in kleinen Vorschauen die Dichte und den Detailgrad an. Die Windungen setzen einander fort. Ein Kapitel kann über mehrere Windungen reichen und innerhalb einer Windung enden. Die Karte zeigt Ausdehnung und Reihenfolge entlang der Spur.

Verwende eine monotone Abbildung der Sequenzposition auf die **Weglänge** entlang der Spirale. Bei fester Skalierung belegen gleich lange Abschnitte gleich viel Weg. Erzeuge aus der Geometrie eine Weglängentabelle oder eine gleichwertige Abbildung für Zeichnen und Rückprojektion. Bei Klick, Berührung oder Zeigerbewegung muss ein Treffer die nächstgelegene Spurposition im Trefferbereich liefern. Beim Ziehen hilft die bisherige Spurposition dabei, versehentliche Sprünge auf die benachbarte Windung zu vermeiden. Erlaube zusätzlich den genauen Sprung über Eingabefeld oder Inhaltsverzeichnis. Anfang, Ende, Cursor und Bereichsauswahl sind visuell verschieden. An einer gemeinsamen Grenze bleiben alle Tags im Inspektor erreichbar.

Mache Hierarchie durch Größe, Gewicht und Form der Zeichen ablesbar. Farbe kann Bereiche und Materialeigenschaften tragen. Akt- oder Kapitelgrenzen bleiben auch ohne Farbe zu unterscheiden. Beim Zoom treten je nach Dichte feinere Tags und Inhaltsmerkmale hervor. Die Auswahl wird als Bereich entlang der Spur gezeichnet und kann mehrere Windungen umfassen. Für die kleinen Atlaskarten genügen aggregierte Signatur und wesentliche Grenzzeichen. Die großen Karten bleiben bis in feinere Materialpositionen navigierbar.

### Die Leseseite

Entrollen öffnet eine ganze Leseseite des ausgewählten Kapitels oder der projektspezifischen Seitenebene. Bei fehlender Seitenebene verwende den passenden gröberen Abschnitt. Eine unmarkierte Sequenz erhält eine durchlaufende Leseseite. Das Inhaltsverzeichnis führt in der Reihenfolge zu den übrigen Seiten. Die oberste Ebene zeigt standardmäßig den Akt oder den entsprechenden Hauptteil. Die Kapitelüberschrift gehört zur Leseseite. Eine Szene oder der konfigurierte Absatzrang beginnt einen Absatz.

Ein Absatz besteht aus einer oder mehreren Zeilen derselben Spur. Jede Zeile belegt einen fortlaufenden Sequenzbereich. Sie läuft links nach rechts und setzt sich am linken Rand der nächsten Zeile fort. Ein Wechsel der Fensterbreite ändert den automatischen Zeilenumbruch. Struktur-Tags und die angezeigte Auswahl behalten ihre Position. Eine lange Szene kann über viele Zeilen reichen. Eine kurze letzte Zeile lässt rechts den entsprechenden Freiraum. Pro Profil können sinnvolle Umbruchpunkte gewählt werden, etwa Wort- oder Taktgrenzen. Ein bewusst gesetzter Umbruch steht als eigenes Layoutobjekt an einer eindeutigen Position.

Verwende den gleichen Navigationszustand für Rolle, Leseseite, Inhaltsverzeichnis, Inspektor und Materialansicht. Beim Wechsel zwischen Rolle und Leseseite bleiben die Adresse, der ausgewählte Abschnitt und ein ausgewählter Bereich erhalten. Ein Bereich über mehrere Kapitel bleibt eine Auswahl, während man auf der gerade sichtbaren Seite seinen Anteil sieht. Zeige den Abschnittspfad und die genaue Adresse gut lesbar an. Die Navigation kann eine kurze Entrollanimation verwenden, die die Spurbewegung verständlich macht. Bei reduzierter Bewegung gibt es einen direkten Wechsel. Beim Abspielen von Video folgt die Positionsmarke dem Player. Bei der Wiedergabe einer bearbeiteten Videosequenz springt der Player an Platzierungsgrenzen zu den referenzierten Quellbereichen.

## 8. Der Editor für Umbruch, Gliederung und Montage

Der Editor ist ein Arbeitsraum. Stelle die folgenden Operationen direkt in der Oberfläche bereit. Ein Klick oder Tipp setzt den Cursor. Ziehen, Tastatureingabe oder zwei gesetzte Endpunkte wählen einen Bereich. Eine Zeile, ein Absatz, eine Überschrift und ein Tag können gezielt gewählt werden. Bedienelemente sollen auch beim Arbeiten in einer Leseseite in Reichweite bleiben. Der Inspektor zeigt die Folgen eines Eingriffs, bevor ein größerer Abschnitt verändert wird.

| Aktion | Ergebnis |
| --- | --- |
| **Zeilenumbruch setzen oder entfernen** | Die ausgewählte Position wird als manueller Umbruch gespeichert. Die Seite beginnt dort eine neue Zeile, falls an dieser Position Material folgt. Andere automatische Zeilen können sich neu verteilen. |
| **Seitenumbruch setzen oder entfernen** | Die Leseseite erhält dort eine manuelle Seitenteilung. Das Inhaltsverzeichnis zeigt weiterhin die fachliche Gliederung. Ein umgebrochener Absatz wird als Fortsetzung desselben Abschnitts dargestellt. |
| **Neue Überschrift, neues Kapitel oder neue Szene** | Setze am Cursor eine Marke der gewünschten Ebene. Der bisherige Abschnitt teilt sich entsprechend den Regeln der Hierarchie. Titel und Rang sind bearbeitbar. |
| **Überschrift bearbeiten oder Grenze verschieben** | Ändere Titel, Ebene oder Position. Rolle, Leseseite und Inhaltsverzeichnis rechnen mit derselben neuen Gliederung. |
| **Benachbarte Abschnitte zusammenführen** | Zeige die beiden Abschnitte, die gemeinsame Grenze und betroffene Unterabschnitte. Wähle den beibehaltenen Titel und wie die Unterstruktur weitergeführt wird. Die Aktion entfernt oder ändert die gewählten Strukturmarken. Das Material bleibt in seiner Reihenfolge. |
| **Abschnitt einklappen und wieder öffnen** | Reduziere die angezeigten Details dieses Abschnitts. Sein Bereich bleibt sichtbar und auswählbar. Persönliche Klappzustände können beim Wiederöffnen erhalten bleiben. |
| **Ausschneiden, kopieren, einfügen, duplizieren oder löschen** | Bearbeite einen adressierten Bereich oder einen ganzen Abschnitt. Zeige die Dauer oder Länge und betroffene Struktur vor einer Änderung. |
| **Platzierung teilen, trimmen oder verschieben** | Bearbeite die Referenzen auf das Quellmaterial. Der Nutzer sieht die neuen Grenzen und die resultierende Länge. Vorschau, Rückgängig und Wiederholen stehen für einen vollständigen Eingriff zur Verfügung. |

Ein automatischer Umbruch gehört zur aktuellen Geometrie. Ein gesetzter Umbruch ist eine gespeicherte Anweisung für die Leseseite. Eine Überschrift ist ein Tag in der Sequenz. Eine Montageoperation verändert die Materialbelegung. Zeige diese vier Gegenstände mit unterschiedlichen Aktionen und Symbolen. Das Entfernen einer Kapitelüberschrift und das Löschen ihres Materials brauchen klar getrennte Bedienelemente.

Bei einer Zusammenführung können Unterabschnitte anders enden, weil ihre frühere übergeordnete Grenze entfällt. Berechne diese Folgen im Vorschauzustand. Biete eine Option, eine frühere Grenze mit einem geeigneten feineren Tag zu markieren, wenn sie erhalten bleiben soll. Eine Überschrift lässt sich aus dem Material- oder Strukturinspektor setzen, auch wenn die automatische Analyse dort keinen Kandidaten gefunden hat. Benutzergesteuerte Layoutmarken werden bei einem Schnitt nach derselben Positionsabbildung wie andere sequenzgebundene Elemente bewegt. Automatische Zeilen werden neu berechnet.

### Zeilen und Ausschnitte zwischen Sequenzen kopieren

Die Aktion **Zeile kopieren** erfasst das genaue halboffene Intervall der sichtbaren Zeile im Moment der Auswahl. Speichere im Clip die Quellsequenz und ihre Revision, Profil und Einheit, die zugeschnittenen Platzierungen, die Länge, passende Features und die im Bereich vorhandenen Tags. Erhalte den aktiven Strukturpfad am Anfang als Kontext. Der Inhalt eines kopierten Clips soll auch nach einem Fensterwechsel, neuem Umbruch oder einer Änderung der Ausgangssequenz genau dieselbe Auswahl enthalten. Kopiere Referenzen und Koordinaten. Große Videodateien werden für eine Montage innerhalb desselben Projekts gemeinsam referenziert. Eine explizite Zwischenablage in der App erlaubt den Wechsel zwischen Sequenzrouten. Eine optionale Textkopie im Libretto erhält eine eigene Aktion.

Beim Einfügen an Sequenzposition `p` wird eine dort liegende Platzierung bei Bedarf geteilt. Die gewählten Teile werden eingesetzt und die nachfolgenden Positionen wandern um die Cliplänge nach rechts. Das Einfügen an Position null, mitten in einer Platzierung und am Ende muss funktionieren. Quelladressen bleiben bei der Neuberechnung erhalten. Beginnt an `p` ein vorhandener Ziel-Tag, verschiebt er sich standardmäßig mit dem vorhandenen Zielmaterial. Stelle die Wirkung an Grenzen in der Vorschau sichtbar dar.

Biete folgende Einfügeoptionen an.

- **In Zielstruktur einfügen.** Der Clip wird in die Materialfolge eingefügt. Die Projektgliederung des Ziels bleibt die maßgebliche Struktur. Zielmarken und manuelle Layoutmarken ab der Einfügeposition verschieben sich mit ihrem Material. Der Quellkontext bleibt in der Herkunft des Clips sichtbar.
- **Neue Sequenz aus Auswahl.** Der Clip beginnt bei null. Tags innerhalb der Auswahl werden relativ zum neuen Beginn übernommen. Für bereits laufende Abschnitte kann die App Fortsetzungsüberschriften anlegen. Pro Rang an Position null hat eine ausdrücklich kopierte Marke Vorrang. Der Nutzer kann die resultierende Gliederung vor dem Speichern bearbeiten. Die App erzeugt eine neue Karte.
- **Mit Gliederung einfügen.** Unterstütze zunächst Einfügen an einer H1-Grenze oder am Sequenzende. Der Clip beginnt mit einer eigenen H1-Marke, bei Bedarf aus Titel oder Herkunft abgeleitet. Die App zeigt kopierte und ergänzte Marken vorab an. Nach dem Clip setzt ein vorhandenes nachfolgendes H1 die Zielgliederung fort. Wenn an dieser Stelle eine feinere Zielgliederung läuft, kann der Nutzer den Clip als Material einfügen und die Gliederung bewusst bearbeiten.

Schnitt, Löschen und Verschieben verwenden dieselbe Intervalllogik. Prüfe Überschneidungen mit Tags, Features und manuellen Umbrüchen. Für einen Löschbereich `[a,b)` werden dort liegende Startmarken und Layoutmarken entfernt oder nach ausdrücklicher Auswahl an den Schnittpunkt versetzt. Marken bei `b` gehören zur rechten Seite und werden nach `a` verschoben. Bei einer Kollision muss die Vorschau die Auflösung zeigen. Für quellengebundene Merkmale berechne aus jeder verwendeten Platzierung den sichtbaren Schnitt. Ein explizit sequenzgebundenes Merkmal folgt der Bearbeitung nach einer dokumentierten Regel. Alle Schreibvorgänge erzeugen einen konsistenten Stand und einen gemeinsamen Rückgängig-Schritt.

Bei mehrstimmigem Material wirkt ein Schnitt des Zeitbereichs standardmäßig auf **alle Stimmen**. Die darin enthaltenen Ereignisse bleiben relativ zueinander ausgerichtet. Eine über die Schnittgrenze gehaltene Note oder ein Audioereignis hat im Ausschnitt eine sichtbare Fortsetzung beziehungsweise eine gekappte Dauer. Erhalte im Export oder Inspektor den Quellbezug. Für Musik kann ein Modus an Taktgrenzen einrasten. Ein Clip aus einer Partitur erhält seine Takt- und Stimmenzuordnung. Wenn die Taktstruktur am Ziel wechselt oder Stimmen unterschiedliche IDs haben, zeigt der Inspektor die Zuordnung und behandelt unbekannte Stimmen als neue, eindeutig benannte Stimmen oder lässt den Nutzer sie zuordnen. Vorhandene und neue Taktfragmente müssen darstellbar bleiben. Eine Einzelstimme kann separat angezeigt oder ausgewählt werden. Das Einfügen einer einzelnen Stimme als zusätzliche parallele Spur kann nach dem gemeinsamen Schnittmodell als eigene Operation hinzukommen.

Erlaube in der ersten produktiven Version das Kopieren und Einfügen zwischen kompatiblen Sequenzen desselben Projekts. Eine RNA-Spanne, ein Videoclip und ein Librettoabschnitt liegen in unterschiedlichen Einheiten. Zeige bei unvereinbaren Profilen, warum eine Einfügung als Material nicht möglich ist. Die App kann ihre Referenzen im selben Projekt trotzdem gemeinsam organisieren. Eine spätere profilübergreifende Montage braucht eine ausdrückliche gemeinsame Achse oder eine vorgelagerte Konvertierung.

### Beispiel einer Einfügung

Eine Zeile umfasst die Sequenzpositionen `[12,20)`. Sie besteht aus den letzten drei Einheiten einer Quellplatzierung und den ersten fünf Einheiten der nächsten. Der Clip hat Länge acht und zwei exakt zugeschnittene Platzierungen. Füge ihn an Position vier der Zielsequenz ein. Der eingefügte Ausschnitt belegt dort `[4,12)`. Das zuvor ab Position vier vorhandene Material beginnt bei zwölf. Wenn der Browser nach dem Kopieren schmaler wird, bleibt der Clip acht Einheiten lang. Rückgängig stellt die frühere Belegung und Gliederung in einem Schritt wieder her.

## 9. Architektur, Persistenz und Qualität

Entwickle den vorhandenen Angular-Client, die Flask-API und die PostgreSQL- und Celery-Infrastruktur aus Abschnitt 0 zu einem vollständigen Web-Stack weiter. Modernisiere zuerst die für den durchgehenden Videofall benötigten Abhängigkeiten und dokumentiere die funktionierende Kombination. Nutze den vorhandenen Worker für die dauerhafte Verarbeitung von Importen und Analysen. Führe Datenbankänderungen als Migrationen aus. Verwende eine lokal startbare Materialablage mit klarer Schnittstelle zu privatem Objektspeicher. Medien- und Geometriefunktionen sollen unabhängig von UI und Datentransport testbar sein.

Modelliere Schreiboperationen als nachvollziehbare, atomare Revisionen oder gleichwertige Transaktionen. Die Bearbeitung kennt die Ausgangsrevision. Konflikte bei zwei gleichzeitig offenen Browsern werden erkannt. Zeige den lokalen Bearbeitungsstand und biete erneutes Anwenden auf die aktuelle Version oder das Sichern als Kopie an. Weise nach Speichern, Netzwerkfehler und Validierungsfehler einen eindeutigen Zustand aus. Rückgängig und Wiederholen arbeiten auf Bearbeitungsschritten. Die Ansicht eines älteren Stands und das Wiederherstellen einer Revision müssen eine konsistente Belegung liefern. Speichere persönliche UI-Einstellungen getrennt von gemeinsam bearbeiteter Struktur.

Prüfe beim Löschen einer Quelle, ob Sequenzen sie referenzieren. Zeige ihre Verwendung. Ein Archiviermodus oder eine ausdrücklich bestätigte, konsistente Entfernung soll versehentliche Datenlücken vermeiden. Analyseergebnisse sind an die Quelle oder an die konkrete Revision gebunden. Eine vorgeschlagene Marke, die sich auf eine alte Quellstelle bezieht, kann bei mehreren Verwendungen gezielt einer Verwendung zugeordnet werden.

Für lange Sequenzen rendere keine Notiz, kein Bild und kein DOM-Element je möglicher Position. Verwende Aggregatdaten in mehreren Detailstufen, ausschnittweises Laden, sichtbarkeitsabhängiges Nachladen und bei Bedarf virtuelle Zeilen. Die Atlasübersicht lädt kleine vorberechnete Signaturen. Die große Rolle fragt feinere Segmente nach. Die Leseseite berechnet nur sichtbare oder bald sichtbare Bereiche. Inhaltsverzeichnis, Seiten und Quellsuche nutzen indizierte Positionen. Teste einen Fall mit vielen tausend Tags oder Ereignissen und einen langen Medienfall. Miss auf dokumentierter Testumgebung, wie schnell Atlas, großer Kreis und erster Detailausschnitt nutzbar werden. Der Player bewegt die Positionsmarke ohne Neuaufbau der Seite.

Der GUI-Entwurf setzt den Fokus auf die Kreisfläche und die Lesbarkeit der Seite. Verwende klare Typografie, sichtbare Fokuszustände, verständliche Einheiten und ruhige Werkzeuge am Rand. Rollenansicht und Leseseite unterstützen Tastatur, Maus und Touch. Biete für die Kreisinteraktion eine zugängliche alternative Positionswahl. Überfrachtete Karten werden bei Bedarf mit Zoom und auswählbaren Merkmalsebenen lesbar. Leere, noch ladende und fehlerhafte Zustände brauchen konkrete nächste Schritte.

## 10. Lieferumfang und Abnahme

Liefere im Repository eine ausführbare Anwendung mit reproduzierbarem Start, Datenbankmigrationen, dokumentierten Umgebungsvariablen, Beispielprofilen, Beispieldateien und Tests. Erzeuge eine Demo mit Video, RNA, Libretto und polyphoner Partitur im selben Atlas. Verwende für die Demo selbst erzeugtes oder eindeutig zur Weitergabe geeignetes Material. Die Beispielgliederung ist als solche beschriftet. Die RNA-Karte soll die Bildreferenz in Komposition und Funktion erkennbar aufnehmen. Verwende für eine wissenschaftlich beschriftete Karte und für echte Opernzeitmarken die tatsächlich zugehörige, versionierte Quelle.

Baue in vertikalen Schritten. Zuerst startet der aus Video Score übernommene Videopfad reproduzierbar mit einer kleinen lokalen Testdatei. Danach funktionieren Anmeldung, Projekt, Atlas, Import einer Video- und einer diskreten Sequenz, persistierte Karten und der Wechsel in den Editor. Ergänze Gliederungs- und Montageoperationen, die weiteren Startprofile, weitere Materialdarstellungen und Revisionen. Implementiere die Berechtigungsprüfung jeweils zusammen mit den betreffenden Funktionen. Schließe den Bauauftrag mit den folgenden End-to-End-Abläufen ab.

1. **Öffnen und orientieren.** Nach der Anmeldung öffnet sich der Atlas eines zugänglichen Projekts. Er zeigt Kreiskarten für Video, RNA, Libretto und Partitur. Jede Karte nennt Typ, Länge und passende Einheit. Ein leeres Projekt zeigt eine verständliche Importaktion.
2. **Echtes Material importieren.** Lade ein Video hoch und importiere eine Datei über einen unterstützten Direktlink. Zeige die Quelle und den Analysefortschritt. Nach der Verarbeitung ist die Karte aus dem tatsächlichen Material erreichbar. Ein fehlerhafter Link und ein Wiederholungsversuch haben nachvollziehbare Zustände.
3. **Mit Originaleinheiten arbeiten.** Importiere FASTA, ein Libretto und MusicXML. Prüfe Adressierung, Darstellbarkeit und Auswahl in Basen, Wörtern und musikalischer Position. Ein Formatwechsel innerhalb des Projekts setzt keinen Player voraus.
4. **Struktur aus Tags lesen.** Setze mehrere Rangstufen an dieselbe Position und später einen Kapitelbeginn. Rolle, Inhaltsverzeichnis und Seite geben dieselbe Verschachtelung wieder. Ein überlappendes RNA-Merkmal bleibt unabhängig sichtbar.
5. **Eintauchen.** Wähle eine Stelle in der Kreisübersicht. Öffne dieselbe Stelle in der großen Karte und entrolle die dazugehörige Seite. Zoome bis zu den zugehörigen Basen, Worten, Bildern oder Noten. Rolle wieder auf und finde die Auswahl wieder.
6. **Umbruch und Gliederung editieren.** Setze einen manuellen Zeilen- und Seitenumbruch. Füge ein Kapitel ein, ändere die Überschrift, verschiebe die Grenze und führe zwei benachbarte Abschnitte zusammen. Ändere die Fensterbreite. Die gesetzten Umbrüche und gewählten Strukturadressen bleiben reproduzierbar. Ein Rückgängig-Schritt macht die jeweilige Aktion rückgängig.
7. **Neu montieren.** Kopiere eine Zeile über eine Platzierungsgrenze hinweg. Ändere die Fensterbreite. Füge sie in eine andere kompatible Sequenz mitten in einer Platzierung ein. Prüfe Clipgrenzen, Quelladressen, Positionen des folgenden Materials und die aktuelle Gliederung. Lege aus einem ganzen Kapitel zusätzlich eine neue Karte an.
8. **Gleichzeitigkeit erhalten.** Importiere eine Partitur mit einem Akkord, mindestens zwei Stimmen und einer über eine Zeilengrenze gehaltenen Note. Gleichzeitige Noten stehen an derselben Achsenposition. Kopiere den Bereich mit allen Stimmen in eine zweite Partitur und prüfe gleiche Einsatzabstände, Fortsetzungen und dieselbe Reihenfolge der Takte.
9. **Persistenz und Zugriff prüfen.** Lade die bearbeitete Sequenz nach erneutem Login. Prüfe gespeicherte Gliederung, Belegung und Rückkehr zur letzten Position. Prüfe, dass ein Leser sehen kann und serverseitig keine Schreibrechte erhält. Eine fremde Projekt-ID verleiht keinen Zugriff auf Vorschauen oder Quelldaten.
10. **Übernahme aus Video Score prüfen.** Öffne ein migriertes Videodokument mit mehreren referenzierten Ausschnitten. Verifiziere ihre ursprüngliche Reihenfolge, den ersten und letzten Frame, die Zuordnung zum OM-Bild und die Position auf der Kreiskarte. Prüfe dieselbe Medienverarbeitung mit einem neuen Upload.
11. **Austausch und Robustheit prüfen.** Exportiere eine bearbeitete Sequenz und importiere sie mit zugeordneten Quellen erneut. Verifiziere Länge, Tags und Quellbezug. Prüfe Wiederanlauf eines Analysejobs, parallele Änderungen und Karten mit sehr vielen Ereignissen.

Halte im README Start, Datenfluss, Importformate, Koordinatenkonventionen und Bedienung knapp fest. Füge eine kleine reproduzierbare Testsammlung für den Tag-Algorithmus, die geometrische Positionstreue, den Umbruch, die Schnittoperationen, mehrstimmige Ereignisse und die Rollenprüfung bei. Zeige den laufenden oder lokal ausführbaren Stand mit den tatsächlichen Startbefehlen und den Ergebnissen der ausgeführten Prüfungen.
