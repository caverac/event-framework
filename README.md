# Event Framework

A Whitehead-inspired Domain-Driven Design framework — *"From Philosophical Cosmology to Software Design."*

## Table of Contents

- [Install & Sync Dependencies](#install--sync-dependencies-uv)
- [Documentation Site](#documentation-site)
- [Project Layout](#project-layout)
- [Design principles](#design-principles)
- [Development](#development)
  - [Run tests & linters](#run-tests--linters)
  - [Using `virtualenvwrapper` with `uv`](#using-virtualenvwrapper-with-uv)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [License](#license)



## Install & Sync Dependencies (`uv`)

```bash
# 1) Clone
git clone https://github.com/caverac/event-framework.git
cd event-framework

# 2) Create local env (optional; uv will create .venv automatically on sync)
uv venv .venv

# 3) Install runtime + dev + docs groups
uv sync --all-groups

# 4) Run tests
uv run pytest -q
```


## Documentation Site
Narrative docs + examples live under docs/ and publish via GitHub Pages.

Build the site

```bash
uv run mkdocs build --strict
```

and serve locally with live reload:

```bash
uv run mkdocs serve
```

The currently deployed site is at: https://caverac.github.io/event-framework/


## Project Layout

```bash
cosmology-to-software/
├─ pyproject.toml
├─ src/
│  └─ event_framework/
│     ├─ __init__.py
│     ├─ core.py
├─ tests/
│  └─ unit/
│     └─ event_framework/
│        └─ test_core.py
├─ docs/
│  ├─ index.md
│  ├─ getting-started.md
├─ mkdocs.yml
└─ .github/workflows/
   └─ docs.yml
```

## Design principles
- Process-first modeling: State changes result from explicit decision processes (occasions).
- Typed invariants: Ingress domain rules as value objects you can test in isolation.
- Events as superjects: Every decision yields externally visible consequences.
- Composable nexus: Relations across bounded contexts are modeled, not hidden.
- Narrative documentation: Executable examples tell the story alongside the API.

## Development

### Run tests & linters

```bash
uv run pytest -q
uv run pylint src tests
uv run black --check src tests
uv run mypy src tests
```

## Using `virtualenvwrapper` with `uv`

If you already hace an active `virtualenvwrapper` setup, you can tell `uv` to use it instead of creating its own `.venv`:

```bash
workon projects@cosmology-to-software
uv sync --all-groups --active
```

Or tell uv to treat that env as the project env:

```bash
export UV_PROJECT_ENVIRONMENT="$HOME/.virtualenvs/<virtual-env-name>"
uv sync --all-groups
```

## Contributing
1. Fork the repo and create a feature branch.
2. Add tests for new behavior.
2. Run formatters/linters and ensure coverage is not reduced.
3. Open a PR with a concise description and a short example of the new concept/abstraction.

## Roadmap
- [ ] Versioned releases & changelog
- [ ] More examples (e-commerce, banking, IoT, etc.)

## License
MIT License. See [LICENSE.md](LICENSE.md) file for details.
