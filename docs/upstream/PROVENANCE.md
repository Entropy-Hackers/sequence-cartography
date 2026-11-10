# Herkunft des übernommenen Codes

| | |
|---|---|
| Quelle | [human-centered-ai-lab/app-video-score](https://github.com/human-centered-ai-lab/app-video-score) („Video Score") |
| Übernommener Commit | `6383f18164a96c64a80de15ebba00b4559842ce4` (`master`, „update to new ubuntu", 2023-10-19) |
| Art der Übernahme | Git-Merge mit vollständiger Historie (`git merge --allow-unrelated-histories video-score/master`) auf dem Zweig `integrate/video-score` |
| Remote | `video-score` → `https://github.com/human-centered-ai-lab/app-video-score.git` |
| Lizenz | MIT, Copyright (c) 2017 Heimo Müller, Medical University Graz. Siehe [`LICENSE`](../../LICENSE). |

Der Originalinhalt des Video-Score-README liegt unverändert in [`video-score-README.md`](video-score-README.md).

Folgende Teile von Video Score sind bewusst **nicht** im Repository:

- `data/`: Mediendateien, Caches und Postgres-Daten (laut Upstream-`.gitignore` nie versioniert)
- `client/node_modules/`, `nodejs-server/node_modules/`
- eine im lokalen Arbeitsstand angefangene, nicht committete Änderung am `server/Dockerfile` (Umstellung auf `ubuntu:20.4`)

Der frühere Prototyp von 2018/19 (VIDEO-ANALYZER) liegt unter [`legacy/`](../../legacy/).
