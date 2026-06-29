# CLAUDE.md

Guidance for working in this repository. The conventions below are inferred from the
existing code — follow the surrounding code when something here is unstated, and where a
rule is an assumption rather than an enforced standard it is called out explicitly.

## Project overview

`addons-release-tests` is the end-to-end UI/API test suite for the
[Mozilla Add-ons site (AMO)](https://addons.mozilla.org), maintained mostly by the AMO QA
team. Its goal is to reduce the manual regression suite that runs weekly on the AMO
**staging** environment before each production release.

- **Language:** Python (CI runs on Python 3.14; some webext jobs invoke 3.11).
- **Browser:** Firefox **Nightly** is required for dev/stage runs (signed add-ons use
  dev-root certs that release Firefox rejects). Prod install tests use a release-style setup.
- **Driver:** geckodriver / Selenium 4.
- **Coverage areas:** frontend site (home, search, detail, install, ratings, collections,
  users, themes, blog, language tools), Developer Hub (devhub home, add-on edit/validate,
  submissions), reviewer tools, REST API, and `webext` browser-chrome behaviour.

## Repository structure

```
pages/desktop/          PyPOM Page Objects, one module per AMO area
  base.py               Base page + shared Header / Footer / SearchBox regions
  frontend/             Frontend site pages (home, search, details, collections, ...)
  developers/           Developer Hub pages (devhub_home, submit_addon, edit_addon, ...)
  reviewer_tools/       Reviewer tools pages
  toolbar/              Firefox toolbar page object (about:addons etc.)
regions/desktop/        Reusable PyPOM Regions shared across pages (shelves, categories, ...)
tests/                  Test modules grouped by area (mirrors pages/)
  conftest.py           All shared fixtures live here (single conftest)
  frontend/  devhub/  devhub_submissions/  reviewer_tools/  api/  api_w/  webext/  coverage/
scripts/                Non-page helper utilities (reusables, waits, shadow DOM, kbd, install)
api/                    API test helpers: api_helpers.py, payloads.py, responses.py
sample-addons/          Add-on artifacts used as test inputs (.zip/.xpi/.crx, manifest.json)
img/                    Image fixtures (icons, screenshots, profile pictures)
dev.json stage.json prod.json   Per-environment variables (pytest-variables)
translations.json       Locale/translation expectations passed via --variables
pytest.ini setup.cfg    pytest config and marker registration
.circleci/config.yml    CI definition (jobs + workflows)
.pre-commit-config.yaml  Formatting hooks (black, double-quote-string-fixer)
```

`*-results.html` files at the repo root are committed pytest-html reports from past runs;
they are artifacts, not source. `<user>.txt` files (e.g. `api_user.txt`) hold session
cookies written by the login fixture — see Authentication below.

## Development commands

```bash
# Install dependencies (use a venv)
pip install -r requirements.txt          # runtime + test deps
pip install -r requirements.dev.txt      # adds pre-commit

# Formatting / linting (pre-commit hooks)
pre-commit install
pre-commit run --all-files
```

Formatting is enforced by **black** with `--skip-string-normalization` plus the
`double-quote-string-fixer` hook. `pylint`/`isort` are installed as dependencies but there
is no project config wiring them into CI — black + pre-commit are the source of truth.

## Testing commands

The runner is **pytest** with **pytest-selenium**. Tests require `--driver` and at least one
`--variables` (environment) file.

```bash
# Whole suite area against staging
pytest tests/frontend --driver Firefox --variables stage.json

# Frontend tests also need translations.json (CI passes both)
pytest tests/frontend --driver Firefox --variables translations.json --variables stage.json

# One file / one test
pytest tests/frontend/test_search.py --driver Firefox --variables stage.json
pytest tests/frontend/test_search.py::test_name --driver Firefox --variables stage.json

# Pick by marker
pytest tests/frontend -m "not serial and not prod_only" --driver Firefox --variables stage.json
pytest tests/frontend/test_ratings.py -m "serial"        --driver Firefox --variables stage.json

# Parallel (xdist) + rerun flaky tests, headless — matches CI
MOZ_HEADLESS=1 pytest tests/devhub -n 4 --reruns 2 --driver Firefox --variables stage.json

# HTML report
pytest ... --html=results.html --self-contained-html

# Remote (selenium-standalone in Docker)
pytest <test> --driver Remote --port 4444 --capability browserName firefox --variables stage.json
```

Environment selection is purely the `--variables` file: `stage.json` (default target),
`dev.json`, `prod.json`. `base_url` and all reusable test data come from that file via the
`variables` fixture.

## Coding standards

- **Formatting:** black, string normalization **off**; `double-quote-string-fixer` is
  configured. The codebase is mixed — newer modules (`tests/conftest.py`, `pages/desktop/base.py`)
  use double quotes while older ones (`scripts/reusables.py`, `regions/`) use single quotes.
  **Assumption:** match the quote style already used in the file you are editing rather than
  reformatting the whole module.
- **Imports:** grouped stdlib → third-party (`pytest`, `selenium`, `pypom`, `requests`) →
  local (`pages…`, `regions…`, `scripts…`, `api…`). To break circular imports, Page Objects
  import the *next* page **inside the navigation method** (see `pages/desktop/base.py`
  `click_extensions`), not at module top. Keep this pattern.
- **Docstrings:** module- and method-level docstrings explaining *why* (especially the
  Firefox/Selenium quirk being worked around) are common and expected; preserve that style.
- **Comments:** explain non-obvious browser behaviour (stale elements, hover/dropdown timing,
  chrome vs content context, restricted-domain prefs). The repo favours explanatory comments
  over terse code.

## Testing guidelines

- **One test file per site area**, placed in the matching `tests/<area>/` subfolder.
- **Test function naming:** `test_<description>_tc_id_c<NNNN>` where `cNNNN` is the TestRail
  case ID (e.g. `test_search_suggestion_term_is_higher_tc_id_c4481`). Newer tests sometimes
  omit the id; include it when a TestRail case exists.
- **Signature:** tests take fixtures as arguments — typically `base_url, selenium` and add
  `variables` when they read test data. Pull expected values from `variables[...]`, do not
  hardcode strings that differ across environments.
- **Markers** (register any new marker in `pytest.ini` to avoid warnings):
  - `serial` — must run alone (interdependent / stateful); excluded from parallel jobs.
  - `sanity` — eligible for the prod sanity run.
  - `prod_only` — runs only against prod; excluded from stage runs.
  - `nondestructive` — safe, read-only test.
  - `firefox_release` — prod install tests that skip dev prefs.
  - `login("<user>")` — start the browser logged in via full FxA flow; writes the session
    cookie to `<user>.txt`.
  - `create_session("<user>")` — start the browser with the stored `sessionid` cookie
    (reads `<user>.txt`).
  - `clear_session` — at test end, invalidate the session via the AMO API and delete the file.
  - Note: some tests use ad-hoc markers like `search`/`webext` that are **not** registered in
    `pytest.ini`. Prefer registering markers you rely on.
- **Assertions:** include a message giving the actual value, e.g.
  `assert x == y, f"Actual status code was {resp.status_code}"`. This is consistent throughout.
- **Flakiness:** CI uses `--reruns 2`. Prefer fixing waits over adding `time.sleep`; a few
  `time.sleep`s exist for autocomplete-style debounce but explicit waits are the norm.

## Page Object conventions (PyPOM)

- **Frameworks:** classes subclass `pypom.Page` or `pypom.Region`. Frontend pages often
  subclass the local `pages/desktop/base.py:Base` (which adds AMO header/footer, login,
  `wait_for_page_to_load`, and shared waits).
- **Class naming:** PascalCase named for the area (`Search`, `DevHubHome`, `Detail`).
- **URLs:** set `URL_TEMPLATE = "developers/"` (relative path) on a page; `Base._url` is
  `"{base_url}"`. Open with `Page(selenium, base_url).open()`.
- **Locators:** module-private class attributes named `_<thing>_locator`, value is a
  `(By.X, "selector")` tuple. Prefer `By.CLASS_NAME`/`By.CSS_SELECTOR`/`By.ID` consistent
  with neighbours.
- **Element access:** expose elements as `@property` that first waits
  (`self.wait.until(EC.visibility_of_element_located(...))`) then returns the element or a
  list of Region instances.
- **Navigation methods:** `click_*` methods perform the action, wait, and **return the next
  Page Object** (imported locally inside the method). Methods that just confirm loading return
  `self` (e.g. `wait_for_page_to_load`).
- **Waits:** use `self.wait` (PyPOM's WebDriverWait, base timeout 30s) with
  `expected_conditions` (imported as `EC`, sometimes `expected`). Add a `message=` to every
  wait so report failures are diagnosable. Use a fresh `WebDriverWait(self.driver, N,
  ignored_exceptions=StaleElementReferenceException)` when an element is known to go stale
  (hover dropdowns, the user menu).
- **Regions:** reusable widgets are `Region` subclasses with a `_root_locator`. Nest closely
  related regions as inner classes (see `Header.SearchBox.SearchSuggestionItem` in `base.py`);
  put broadly reused widgets in `regions/desktop/`.
- **Hover/dropdown interactions:** use `ActionChains` move/pause/click and wait for the
  dropdown to be visible before clicking (see `Header.more_menu`, `click_logout`).

## Fixture conventions

All shared fixtures live in the single `tests/conftest.py`. Key ones:

- `base_url` (session) — returns `variables["base_url"]`; the env file picks the target.
- `firefox_options` — central browser setup. Branches on `base_url`: prod gets a
  release-style profile; dev/stage point `binary_location` at **Firefox Nightly**, enable
  signed-addon dev-root prefs, and (for headless) add `-headless` when `MOZ_HEADLESS` is set.
- `selenium` — parametrized to Desktop `1920x1080`, installs the `waf_bypass_addon`, sets
  window size, and applies the `login` / `create_session` / `clear_session` marker behaviour.
- `waf_bypass_addon` (session) — builds a temporary WebExtension that injects the `fxa-ci`
  header (value from the env var named by `variables["FXA_CI_HEADER"]`) to bypass Fastly/WAF.
  Both `firefox_options` branches clear `extensions.webextensions.restrictedDomains` so this
  add-on can attach its `webRequest` listener on restricted Mozilla domains.
- `session_auth` — reads the stored `sessionid` from `<user>.txt`; used standalone by API
  tests and to seed the browser session.
- `wait` — a ready-made `WebDriverWait` for use inside tests.
- `firefox_notifications` — FoxPuppet notification classes for webext tests.
- `delete_themes` — teardown fixture that removes themes created during devhub theme tests.

When adding a fixture, put it in `tests/conftest.py`, give it the right `scope`, and document
the *why* in its docstring (the existing fixtures explain the browser/pref reasoning).

### Authentication model

Three layers, selected by markers (see above): full FxA login (`login`) which **persists**
the session cookie to `<user>.txt`; cookie reuse (`create_session`) which reads that file;
and cleanup (`clear_session`) which calls `DELETE /api/v5/accounts/session/` and removes the
file. API tests typically read the cookie directly via `selenium.get_cookie("sessionid")`
or the `session_auth` fixture.

## Common utilities (`scripts/`)

- `reusables.py` — `get_random_string(length)`, `current_date()`, `convert_bytes(size)`,
  `scroll_into_view(driver, element)` (fixes `MoveTargetOutOfBoundsException`).
- `custom_waits.py` — custom expected-condition predicates (e.g. `url_not_contains`).
- `shadow_dom.py` — JS-based access into `about:addons` custom-element shadow roots
  (`shadow_query`, `shadow_query_all`, `shadow_visible`, `shadow_click`); Marionette does not
  expose `shadow_root` on Firefox, so these go through `execute_script`.
- `kbd.py` — OS-aware chrome keyboard chords (`send_chord_in_chrome`, `primary_modifier`);
  Firefox chrome commands need chrome-context input and OS-specific modifiers.
- `addon_install.py` — install an arbitrary add-on version via Firefox's `AddonManager` from
  the Marionette chrome context (for the update flow that the UI cannot reach).

API helpers live under `api/`: `payloads.py` (request bodies), `responses.py` (expected
shapes), `api_helpers.py` (`make_addon`, `verify_addon_response_details`, ...). API tests use
`requests` directly against `f"{base_url}/api/v5/..."`.

## CI considerations (CircleCI)

- **Executors:** most jobs run on the `cimg/python:3.14-browsers` Docker image and install
  **Firefox Nightly** from the Mozilla APT repo with `DISPLAY=:99`; the coverage-devhub job
  runs on the Windows executor.
- **Standard env per job:** `MOZ_HEADLESS: 1` (where applicable) and
  `PYTEST_ADDOPTS: -n <N> --reruns 2`. Parallel suites use `-n 4`; serial suites use `-n 1`.
- **Workflows:**
  - `commit_workflow` — runs on every non-scheduled pipeline (frontend, devhub, submissions,
    plus the serial collections/ratings/user jobs).
  - Scheduled workflows (configured in the CircleCI UI): `scheduled_stage_release_run`,
    `scheduled_dev_regression_tests`, `scheduled_prod_sanity_run` (gated by a manual
    `hold`/approval step), `scheduled_coverage_run`, `scheduled_reviewer_tools_run`,
    `scheduled_webext_release_stage_run`.
- **Granularity:** serial suites (collections, ratings, users) get their own jobs so a flaky
  serial area doesn't block the parallel ones. Keep new serial-heavy areas in dedicated jobs.
- **Dependabot** is limited to **one open pip PR at a time** on purpose — concurrent dependency
  jobs running interdependent tests cause failures.

## Browser-specific notes

- Dev/stage **require Firefox Nightly**; the `firefox_options` fixture locates the Nightly
  binary explicitly (macOS `/Applications/Firefox Nightly.app`, Windows
  `C:\Program Files\Firefox Nightly`, CI `/usr/bin/firefox-nightly`) so Selenium doesn't pick
  the release Firefox on `PATH`.
- `about:addons` UI is built from Mozilla custom elements; reach into their shadow DOM with
  `scripts/shadow_dom.py`, not normal `find_element`.
- Chrome-level actions (Add-ons Manager shortcut, install door-hangers, `installAddonFromAOM`)
  require switching Marionette to **chrome context** (`driver.context(driver.CONTEXT_CHROME)`)
  — see `scripts/kbd.py` and `scripts/addon_install.py`.
- `webext` tests drive browser chrome via **FoxPuppet** (`firefox`, `firefox_notifications`
  fixtures) and run non-headless behaviour against installed Firefox.
- Fastly/WAF on AMO is bypassed by the `waf_bypass_addon` injecting an `fxa-ci` header; this
  is why `restrictedDomains` is cleared in `firefox_options`.

## Things to avoid

- Don't hardcode environment-specific values (URLs, names, copy) in tests — read them from the
  `--variables` JSON via the `variables` fixture.
- Don't add bare `time.sleep` to fix timing; use `self.wait`/`WebDriverWait` with an
  `expected_condition` and a `message=`.
- Don't import the next Page Object at module top-level inside `pages/` — import it inside the
  navigation method to avoid circular imports.
- Don't introduce a marker without registering it in `pytest.ini`.
- Don't add a second `conftest.py` for shared fixtures — keep them in `tests/conftest.py`.
- Don't reformat an existing module's string quotes wholesale; match the file's existing style.
- Don't commit secrets — FxA/CI header values come from environment variables, never the repo.
- Don't edit the root `*-results.html` reports; they are generated artifacts.

## Best practices specific to this project

- Mirror the directory layout: a new frontend page object goes in `pages/desktop/frontend/`
  and its tests in `tests/frontend/`.
- Keep navigation chains fluent: `Page(...).open().wait_for_page_to_load()`, and have
  `click_*` return the destination page object so tests read top-to-bottom.
- Always attach a descriptive `message=` to waits and a value-bearing message to asserts —
  the HTML report is the primary debugging tool.
- Decide a test's marker(s) deliberately: `serial` vs parallel-safe, and whether it is
  `sanity`/`prod_only`/`nondestructive`; this directly determines which CI job runs it.
- When a workaround exists for a Firefox/Selenium quirk, document the reason in a comment or
  docstring as the surrounding code does.

---

### Notes / assumptions for maintainers

- The `README.md` mentions mobile + desktop resolutions, but `tests/conftest.py` currently
  parametrizes the `selenium` fixture for **Desktop (1920x1080) only**. Treat Desktop as the
  active target unless the fixture is changed.
- `users.json` referenced in the README is not in the repo; authentication now flows through
  the `login`/`create_session` markers and `<user>.txt` session files.
- The pre-commit black hook pin is `rev: stable` (deprecated); the codebase shows quote-style
  drift, so file-local consistency is the practical rule.
