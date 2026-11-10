# Sequence Cartography

An atlas for long, ordered sequences: videos, RNA/DNA, libretti and music scores become circular maps (spiral rolls) that you can dive into, unroll into reading pages, structure with headings, and re-assemble.

**Status:** architecture phase. The code base is [Video Score](docs/upstream/PROVENANCE.md) (Angular + Flask + PostgreSQL + Celery), merged with its full git history. It is being modernized step by step towards the product described in the [build specification](docs/spec/Bauprompt_Sequenzrolle_und_Leseseite.md) (German).

| Document | Content |
|---|---|
| [docs/architecture.md](docs/architecture.md) | Analysis of the existing code, target architecture, data model, milestones |
| [docs/spec/](docs/spec/) | Build specification |
| [docs/upstream/](docs/upstream/) | Provenance and original README of Video Score |

## Repository layout (current)

| Path | Origin | Content |
|---|---|---|
| `client/` | Video Score | Angular 9 / NgRx client |
| `server/` | Video Score | Flask API, Celery tasks, SQLAlchemy models, vendored PySceneDetect |
| `nginx/`, `postgresql/`, `docker-compose*.yml`, `.env` | Video Score | Container setup (BIBBOX app) |
| `src/seqcarto/` | new (2026) | Modernized video analysis library and CLI: scene cuts, slit-scan, OM images, local viewer |
| `tests/` | new (2026) | Tests for `seqcarto` |
| `legacy/` | VIDEO-ANALYZER 2018/19 | First prototype, kept as historical material |

## Video analysis library (seqcarto)

```bash
uv sync
uv run seqcarto analyze path/to/video.mp4 [--end SECONDS]   # scenes, OM images, manifest.json in ./output
uv run seqcarto view                                         # local viewer on http://127.0.0.1:8765/
uv run pytest
```

## License

MIT, see [LICENSE](LICENSE).
