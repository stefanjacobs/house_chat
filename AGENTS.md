# Repository Guidelines

## Project Structure & Module Organization
- Entry point: `app.py` runs the Telegram bot and scheduled tasks.
- Core modules in `src/`: `scheduler.py`, `telegram_handlers.py`, `ai_responses.py`, `ai_prompts.py`.
- Feature tools in `src/tools/` (e.g., `src/tools/weather_app.py`, `src/tools/news_app.py`, `src/tools/car_app.py`). Shared utilities in `src/toolbox/`.
- State/data in `database/`. Archived materials in `archive/`.
- Packaging & dependencies via `pyproject.toml` (Poetry) and `poetry.lock`.

## Build, Test, and Development Commands
- Install deps: `poetry install`
- Run locally: `poetry run python app.py`
- Env vars: set secrets in `.env` or `.envrc` (loaded via `python-dotenv`). Examples: `TELEGRAM_TOKEN=...`, `OPENAI_API_KEY=...`.
- Tests (if present): `poetry run pytest`

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation.
- Use `snake_case` for files/functions, `CapWords` for classes.
- Keep module names descriptive (e.g., `telegram_user_data.py`); prefer explicit imports within `src/`.
- Include docstrings for public functions/classes and type hints where feasible.
- No enforced formatter; keep consistent style. If using tools locally, prefer Black and Ruff.

## Testing Guidelines
- Use `pytest`; place tests under `tests/` named `test_*.py`.
- Cover critical paths: `src/scheduler.py`, `src/tools/*`, and `src/telegram_handlers.py`.
- Mock external APIs (Telegram, OpenAI, HTTP requests) to keep tests deterministic.

## Commit & Pull Request Guidelines
- Commit messages: present-tense, imperative, concise (e.g., Update for evcc URI change; Fix DWD warning parsing).
- Pull requests include:
- Clear description and rationale
- Linked issue (if applicable)
- Logs or screenshots of Telegram flows/output
- Notes on config or migration impacts (env vars, DB files)

## Security & Configuration Tips
- Never commit secrets. Use `.env`/`.envrc`; avoid hardcoded tokens.
- Keep SQLite/state files in `database/`; back up if needed.
- Review dependency changes in `pyproject.toml`; run `poetry update` cautiously.
