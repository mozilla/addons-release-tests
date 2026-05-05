# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Selenium-based UI and API test suite for the [Mozilla Addons website (AMO)](https://addons.mozilla.org). Tests validate pre-release AMO deployments against staging and production environments.

## Setup

```bash
pip install -r requirements.txt
```

Requires geckodriver on `PATH` and Firefox Nightly installed locally for foreground runs.

## Running Tests

### Full suite against staging (foreground)
```bash
pytest --driver Firefox --variables stage.json --variables users.json
```

### Single test file
```bash
pytest tests/frontend/test_search.py --driver Firefox --variables stage.json --variables users.json
```

### Single test
```bash
pytest tests/frontend/test_search.py::test_name_of_choice --driver Firefox --variables stage.json --variables users.json
```

### Against production
```bash
pytest --driver Firefox --variables prod.json --variables users.json
```

### Headless (Docker/Selenium-standalone on Windows)
```bash
docker image build -t firefox-standalone:latest .
docker run -p 4444:4444 --shm-size 2g --rm firefox-standalone:latest
pytest tests/frontend/test_search.py --driver Remote --port 4444 --capability browserName firefox --variables stage.json
```

### CI-style parallel run
```bash
pytest -n 4 --reruns 2 --driver Firefox --variables stage.json
```

## Lint / Format

```bash
black .
pylint tests/ pages/ api/ scripts/
pre-commit run --all-files
```

## Architecture

### Layer overview

```
tests/          # pytest test functions — thin, use page objects and fixtures
pages/          # Page Object Model (PyPOM) — one class per page/region
regions/        # Reusable sub-page regions (nav, modals, etc.)
api/            # Direct HTTP helpers (requests library) for API tests
scripts/        # Custom Selenium waits and shared helper utilities
sample-addons/  # .xpi/.zip files used as fixtures in upload/install tests
```

### Page Object Model

All UI interaction lives in `pages/desktop/` — never in test files. Pages extend PyPOM `Page`; sub-components extend `Region`. The three sub-trees mirror the three site areas:

- `pages/desktop/frontend/` — public AMO site (search, home, details, reviews, collections, users)
- `pages/desktop/developers/` — Developer Hub (submit, edit, manage versions, validate)
- `pages/desktop/reviewer_tools/` — Reviewer queue pages

`pages/desktop/base.py` defines shared `Header` and `Footer` regions inherited by all pages.

### Key fixtures (`tests/conftest.py`)

| Fixture | Scope | Purpose |
|---|---|---|
| `selenium` | function | Core WebDriver; installs WAF bypass addon; applies window size; handles login markers |
| `waf_bypass_addon` | session | Builds a temporary WebExtension that injects `fxa-ci` header — required to hit staging behind WAF |
| `session_auth` | function | Reads a `<user>.txt` file for a stored session cookie |
| `base_url` | session | Pulls `base_url` from the active `--variables` JSON file |
| `delete_themes` | function | Teardown fixture: deletes all themes submitted during a devhub test |

### Authentication flow

Tests use two auth strategies selected by pytest markers:

- `@pytest.mark.login("user_key")` — drives a real FxA browser login and writes the resulting `sessionid` cookie to `<user_key>.txt`
- `@pytest.mark.create_session("user_key")` — reads `<user_key>.txt` and injects the cookie directly, skipping the login UI
- `@pytest.mark.clear_session` — deletes the session via API and removes the `.txt` file in teardown

The `.txt` files are the handoff between `@login` setup tests and `@create_session` usage tests; they must exist before `create_session` tests run.

### Test markers

Defined in `pytest.ini`:

| Marker | Meaning |
|---|---|
| `serial` | Must run with `-n 1`; order-dependent or resource-contending tests |
| `sanity` | Eligible for quick sanity runs on both stage and prod |
| `prod_only` | Excluded from stage release runs (`-m "not prod_only"`) |
| `firefox_release` | Prod install tests; skips dev-only browser prefs |
| `nondestructive` | Safe to run without side effects |

### Variables files

`stage.json`, `prod.json`, `dev.json` — passed via `--variables`; provide `base_url`, addon IDs, FxA credentials, and Firefox preference URLs. `translations.json` holds locale test data. Do not commit credentials; real credentials live outside the repo.

### CI (CircleCI)

`.circleci/config.yml` runs on Windows (`win/default`) with separate jobs for parallel tests, serial tests, API submission/edit tests, sanity, coverage, and reviewer-tool tests. Firefox Nightly is used for stage/dev; Firefox Release for prod.

## Important Constraints

- Tests target both desktop (1920×1080) and mobile (738×414) resolutions — new tests must work at both sizes.
- `xfail_strict = true` in `setup.cfg`: any `xfail` that unexpectedly passes will be treated as a failure.
- The WAF bypass addon (`waf_bypass_addon` fixture) relies on the `FXA_CI_HEADER` env var being set; without it, requests to staging will be blocked.
- Session `.txt` files (e.g. `developer.txt`, `api_user.txt`) are generated at runtime by `@login` tests and consumed by `@create_session` tests — do not add them to git.
