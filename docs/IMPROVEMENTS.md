# AMO Release-Tests — Improvement Audit

*Generated 2026-04-28. All metrics and file:line citations were sampled directly from the working tree at audit time.*

The `addons-release-tests` repo is a mature Selenium/PyPOM suite that has accumulated significant technical debt. This document catalogs ~37 concrete, actionable improvements, prioritized into three buckets.

**Headline findings.**
- 85 `time.sleep()` calls — including a single `time.sleep(500)` (8.3 minutes) inside a 2FA retry loop.
- 213 `@pytest.mark.serial` markers — large blocks of tests cannot be parallelized.
- 28 `@pytest.mark.skip` markers — silently disabled tests, several with reasons like *"update assert"* or no reason at all.
- 8 MB of HTML test reports and 7 plaintext **session-cookie** `.txt` files committed to git, with a 4-line `.gitignore` that doesn't catch them.
- `pages/desktop/frontend/details.py` is 1228 lines with 2 docstrings; the four largest page-object files together total >3700 lines.
- 0% type-hint coverage across `pages/`.
- Dockerfile pins Windows 2004 (long EOL), Selenium 3.141.59, Firefox 66.0.3 — all 2020-era artifacts.

---

## How to read this document

Each improvement uses a fixed template:

> **Problem.** What's broken or sub-optimal.
> **Examples.** Concrete file:line citations.
> **Fix.** Concrete approach.
> **Effort.** S (≤1 dev-day) / M (2–5) / L (>5).
> **Payoff.** Reliability / maintainability / cost / DX.

Priority buckets:

- **P0** — fix now: reliability, security, or correctness risks; cheap wins.
- **P1** — fix this quarter: maintainability, cost, scalability.
- **P2** — opportunistic: nice-to-have polish or strategic modernization.

---

## Table of contents

- [P0 — Reliability, correctness & safety](#p0)
- [P1 — Maintainability & test architecture](#p1-arch)
- [P1 — Tooling & dependencies](#p1-deps)
- [P1 — CI/CD](#p1-ci)
- [P2 — Documentation & developer experience](#p2-docs)
- [P2 — Architecture polish & strategic modernization](#p2-arch)
- [Appendix: metrics snapshot](#appendix)

---

<a id="p0"></a>
## P0 — Reliability, correctness & safety

### 1. Eliminate `time.sleep()` waits across the suite

**Problem.** `time.sleep()` is the dominant synchronization primitive — 85 occurrences across `tests/` and `pages/`. This destroys reliability (sleeps are either too short, causing flakes, or far too long, inflating runtime). Distribution: `sleep(5)` × 50, `sleep(3)` × 10, `sleep(2)` × 10, `sleep(10)` × 6, `sleep(1)` × 3, `sleep(30)` × 2, `sleep(15)` × 1, `sleep(500)` × 1.

**Examples.**
- `pages/desktop/frontend/details.py:54` — `time.sleep(3)` *inside* `wait_for_page_to_load()`, defeating the explicit wait two lines above.
- `pages/desktop/developers/edit_addon.py:63` — `time.sleep(10)` parsing dates.
- `pages/desktop/developers/submit_addon.py:294` — `time.sleep(10)` before upload.
- `pages/desktop/developers/submit_addon.py:921` — `time.sleep(15)`.
- `pages/desktop/developers/manage_versions.py:262` — `time.sleep(30)` in a validation retry loop.
- `tests/frontend/test_search.py:62, 117` — `time.sleep(2)` for autocomplete.

**Fix.**
1. Add `wait_for_*` helpers on `pages/desktop/base.py` for the recurring patterns (loading-spinner gone, tab opened, file-uploaded, validation-complete).
2. Replace each `time.sleep` with a targeted `WebDriverWait(...).until(...)` against an *observable* condition (element visibility, URL change, network idle).
3. For the few places where the wait condition is genuinely unobservable (e.g. third-party widget rendering), introduce a single `_unsynchronized_settle(seconds: float)` helper so the anti-pattern is grep-able and bounded.
4. Add a pre-commit hook (e.g. a `local` regex hook) that fails on new `time.sleep` introductions outside `_unsynchronized_settle`.

**Effort.** L (~5–8 dev-days).
**Payoff.** Major reliability + ~20–40% suite runtime reduction.

---

### 2. Fix the 8-minute `time.sleep(500)` 2FA stall in login

**Problem.** `pages/desktop/frontend/login.py:214` blocks the browser for **500 seconds** (over 8 minutes) when the 2FA code is rejected. The intent was probably to "wait for FxA rate limiting to expire," but in practice this turns a single test failure into a 16-minute multi-test cascade (the loop runs twice).

**Examples.**
- `pages/desktop/frontend/login.py:204-220` — the entire 2FA error block:
  ```python
  for max_retries in range(0, 2):
      if self.is_element_displayed(*self._error_2fa_code_locator):
          time.sleep(500)
          totp = pyotp.TOTP(key)
          ...
  ```
- `pages/desktop/frontend/login.py:207` — separate `time.sleep(30)` after a 2FA-input visibility wait that already returned.

**Fix.**
1. Compute fresh TOTP immediately and retry once; if still rejected, fail fast with a clear assertion message ("FxA 2FA rejected the TOTP — likely a clock-skew or shared-test-account contention issue").
2. Move 2FA seeds to a dedicated test account that no other CI job touches concurrently, eliminating the contention this sleep was masking.
3. If retry-with-backoff is genuinely needed, cap total wait at ~30 seconds and surface the failure via `pytest.fail` rather than silently consuming CI minutes.

**Effort.** S (~½ day).
**Payoff.** Recovers 16+ CI minutes per 2FA failure; clearer diagnostics.

---

### 3. Stop committing test-result HTML and session-cookie `.txt` files

**Problem.** The repo currently tracks ~8 MB of generated test reports plus seven plaintext `.txt` files containing **active session cookies**. This is both a hygiene issue (git history bloats with each test run) and a security issue (cookies committed to a public Mozilla repo, even if expired).

**Examples (all at repo root).**
- `frontend-dev-parallel-test-results.html` — 2.2 MB
- `devhub-parallel-test-results.html` — 2.2 MB
- `submissions-dev-test-results.html` — 1.6 MB
- `coverage-devhub-tests-results.html` — 1.0 MB
- `frontend-parallel-test-results.html` — 1.0 MB
- … plus 6 more HTML files
- `api_user.txt`, `developer.txt`, `reviewer_user.txt`, `reviewer_tools.txt`, `regular_user.txt`, `staff_user.txt`, `submissions_user.txt`, `rating_user.txt`, `collection_user.txt` — each holds a `sessionid` value

**Fix.**
1. Run `git rm --cached` on every `*.html` and `*_user.txt` / `reviewer_tools.txt` etc. at root.
2. Treat the committed cookies as compromised: **rotate** every affected FxA test account and invalidate the corresponding `sessionid` server-side.
3. Apply the `.gitignore` change in [item 4](#item-4) before re-running tests so they don't get re-added.
4. (Optional) Use `git filter-repo` to scrub the cookies from history; if the repo is public this should be done within hours of the cleanup PR.

**Effort.** S (1 day, including the account rotations).
**Payoff.** Security-positive; removes ~8 MB from clones; future test runs no longer dirty the working tree.

---

### 4. Rewrite `.gitignore` <a id="item-4"></a>

**Problem.** The current `.gitignore` is 4 lines and uses literal filenames. It misses every test-result HTML file added after the initial two, every session `.txt` file, `.DS_Store`, and standard Python artifacts.

**Examples.**
- Current full content:
  ```gitignore
  .idea/
  test-results.html
  frontend-parallel-test-results.html
  **/__pycache__/
  ```
- `.DS_Store` is tracked at the repo root (10 KB).
- 11 HTML files match no current rule.
- Seven `*_user.txt` cookie files match no current rule.

**Fix.** Replace with a comprehensive Python/pytest/Selenium ignore:
```gitignore
# OS
.DS_Store
Thumbs.db

# IDE
.idea/
.vscode/

# Python
__pycache__/
**/__pycache__/
*.py[cod]
*.egg-info/
.pytest_cache/
.coverage
htmlcov/

# Virtualenv
.venv/
venv/
env/

# Test artifacts
*.html
!docs/**/*.html
geckodriver.log
selenium.log

# Session cookies (never commit)
*_user.txt
reviewer_tools.txt
developer.txt
```

**Effort.** S (≤1 hour).
**Payoff.** Prevents recurrence of [item 3](#3-stop-committing-test-result-html-and-session-cookie-txt-files); cleanliness.

---

### 5. Resurrect or delete the 28 silently-skipped tests

**Problem.** 28 `@pytest.mark.skip` decorators are scattered through the suite. Many carry no reason; others say things like `"update assert"`, `"need to update way of interaction"`, or `"this test requires more optimization"`. These are dead tests masquerading as coverage — they neither protect anything nor surface failures, but the team carries the maintenance burden.

**Examples.**
- `tests/frontend/test_addon_detail.py:224` — `@pytest.mark.skip(reason="update assert")`
- `tests/frontend/test_addon_detail.py:387, 655` — bare or vague reasons
- `tests/frontend/test_search.py:93` — `@pytest.mark.skip(reason="this test requires more optimization")`
- `tests/frontend/test_versions.py:114, 130, 153` — three consecutive skipped tests
- `tests/frontend/test_home.py:357, 391` — skipped without reason
- `tests/frontend/test_ratings.py:687, 757` — `"update assert"` / no reason
- `tests/frontend/test_sanity.py:36` — skipped sanity test (concerning given sanity's purpose)

**Fix.**
1. Triage each skip into one of: **fix-and-enable**, **delete**, or **convert to documented `xfail`** with a tracked issue.
2. Add a CI check that fails on `@pytest.mark.skip` without a `reason=` argument that begins with `"BUG-"` or a URL.
3. Remove `pytest.mark.skip` entirely from the markers list once the count is ≤ 5.

**Effort.** M (2–4 dev-days, depending on how many revive cleanly).
**Payoff.** Coverage honesty; smaller maintenance surface.

---

### 6. Add assertion messages to bare asserts at boundary tests

**Problem.** Many tests use bare `assert` statements with no message, so a failure produces only `AssertionError` with no context. Worst offender is `tests/frontend/test_install.py`: 17 asserts, 0 with messages. Failures during install tests (which involve browser/addon interaction) are particularly hard to debug without context.

**Examples.**
- `tests/frontend/test_install.py:18` — `assert amo_addon_name == "cas-current-addon-1"` — failure tells you nothing about what was actually loaded.
- Similar patterns across `tests/frontend/test_search.py` (35 bare, 7 messaged).

**Fix.** Adopt a convention:
```python
assert addon.name == expected, f"AMO returned addon name {addon.name!r}, expected {expected!r} (URL: {selenium.current_url})"
```
Add a pylint custom checker or ruff rule (`PT015`) to flag bare asserts in test files going forward.

**Effort.** M (3 days for the worst-offender files; rest can be enforced via lint going forward).
**Payoff.** Faster failure triage in CI logs.

---

### 7. Modernize the Dockerfile

**Problem.** The Dockerfile pins multiple long-EOL artifacts and downloads a binary over HTTPS without a checksum.

**Examples.**
- `Dockerfile:1` — `FROM mcr.microsoft.com/windows:2004` (Windows 10 v2004, EOL Dec 2021).
- `Dockerfile:10-15` — Selenium 3.141.59 (2018), GeckoDriver 0.26.0 (Jan 2020), Firefox 66.0.3 (April 2019).
- `Dockerfile:25-27` — `Invoke-WebRequest` for `selenium-server-standalone.jar` with no integrity check.
- No `USER` directive; container runs as Administrator.

**Fix.**
1. Switch base to `mcr.microsoft.com/windows/servercore:ltsc2022` *or* migrate to a Linux base (preferred — see [item 28](#28-migrate-windows-only-circleci-runners-to-linux)).
2. Bump to current Selenium 4.x grid (or use `selenium/standalone-firefox` from the official Selenium project on Linux).
3. Use `choco install firefox-nightly --version=<pinned>` and parameterize via `ARG`.
4. Add `Invoke-WebRequest` `-Hash` verification step (PowerShell `Get-FileHash`).
5. Drop the manual JAR download in favor of the Selenium `selenium-server` choco package.

**Effort.** M (3–5 days, depending on whether Linux migration is folded in).
**Payoff.** Security; predictable builds; aligns with current Selenium ecosystem.

---

### 8. Pin `pre-commit` hook revisions

**Problem.** `.pre-commit-config.yaml:3` uses `rev: stable` for `psf/black`. The `stable` mutable tag was deprecated in 2022 and pre-commit emits a warning on every run. Builds across machines can pull different black versions, producing diff churn.

**Examples.**
- `.pre-commit-config.yaml:1-6`:
  ```yaml
  - repo: https://github.com/psf/black
    rev: stable
    hooks:
      - id: black
        args: [--skip-string-normalization]
  ```
- `pre-commit-hooks` is pinned to v2.5.0 (2020); current is v4.6+.

**Fix.** Pin `black` to a current tagged release (e.g. `rev: 24.10.0`) and bump `pre-commit-hooks` to `v5.0.0`. See [item 26](#26-expand-pre-commit-hook-coverage) for full hook expansion.

**Effort.** S (≤1 hour).
**Payoff.** Reproducible formatting; quieter CI logs.

---

<a id="p1-arch"></a>
## P1 — Maintainability & test architecture

### 9. Decompose `pages/desktop/frontend/details.py` (1228 lines)

**Problem.** `details.py` is the largest page object in the codebase by far. It mixes the addon header, badges, install button, stats, permissions, reviews summary, and license/EULA dialogs into a single `Detail` class with 151 methods and 2 docstrings. Any change to badges or stats touches the same 1200-line file.

**Examples.**
- File: `pages/desktop/frontend/details.py` (1228 LOC, 151 methods).
- Inline XPath at lines 304, 309, 321, 330 — locators duplicated in method bodies instead of being class-level constants.
- Mix of concerns: `_promoted_badge_locator` (line 24), `_install_button_locator` (line 22), `_privacy_policy_locator` (line 39), and `_block_metadata_message` (line 47) all on the same class.

**Fix.** Split `Detail` into composed regions/sub-pages:
- `AddonHeader` — name, author, icon, summary
- `AddonBadges` — promoted/by-firefox/experimental badges
- `AddonInstallControls` — install button + warnings
- `AddonStats` — user count, ratings count, review count
- `AddonPermissions` — privacy/EULA/license dialogs
- `AddonBlockedMessage` — region-not-available / blocked / why-blocked

`Detail` becomes a thin composition root that exposes these as PyPOM Region attributes.

**Effort.** L (5–8 days, plus migration of all callers).
**Payoff.** Independent edits; faster IDE navigation; testable in isolation.

---

### 10. Decompose the other oversized page objects

**Problem.** Three more files exceed 750 lines each:
- `pages/desktop/developers/submit_addon.py` — 979 lines
- `pages/desktop/frontend/users.py` — 818 lines
- `pages/desktop/developers/devhub_home.py` — 755 lines

`submit_addon.py` is particularly painful: 100+ properties model a multi-step wizard as one class.

**Fix.** Apply the same composition treatment as item 9. For `submit_addon.py`, model each wizard step (`UploadStep`, `DistributionStep`, `MetadataStep`, `ReviewStep`) as its own page, returning the next step from each `submit()` call.

**Effort.** L (one week per file, but can be done file-by-file).
**Payoff.** Clearer page hierarchy; matches the user's mental model of the app.

---

### 11. Reduce XPath usage; eliminate positional indexing

**Problem.** 88 XPath locators vs 533 CSS — roughly 14% XPath. Positional XPath (`[1]`, `[2]`) and `contains(text(), …)` are particularly fragile: any DOM reorder or copy-edit breaks tests with no clear signal.

**Examples.**
- `pages/desktop/frontend/details.py:24` — `"//div[@class='AddonBadges']//div[1]"` (positional)
- `pages/desktop/frontend/details.py:27` — `"…//div[@data-testid='badge-recommended']//span[2]"`
- `pages/desktop/frontend/details.py:42-43` — text-content matching that breaks on translation/copy changes.
- `pages/desktop/reviewer_tools/addon_review_page.py:32-49` — 10+ `//label[contains(text(), '…')]` for sidebar links.

**Fix.**
1. Coordinate with the `addons-frontend` team to add stable `data-testid` attributes where they're missing.
2. Replace `By.XPATH` with `By.CSS_SELECTOR` using `[data-testid='…']` selectors.
3. For positional cases, prefer `:nth-of-type` only when the order is semantically meaningful; otherwise restructure to address elements by attribute.
4. Add a CI check that fails when XPath count rises above the current baseline (ratchet down).

**Effort.** L (M per page-object file; multi-quarter overall).
**Payoff.** Tests survive DOM refactors; failures point at the actual broken element.

---

### 12. Replace inline `find_element(By.XPATH, …)` with class-level `_locators`

**Problem.** A few methods use inline `find_element` calls instead of class-level locator constants. This is an anti-pattern: the locator is invisible to readers scanning the class header, and duplicates leak.

**Examples.**
- `pages/desktop/frontend/details.py:304` — `count = self.addon_user_stats.find_element(By.XPATH, "//div[@class='Badge']//span[2]").text`
- `pages/desktop/frontend/details.py:309, 321, 330` — same pattern.

**Fix.** Promote each inline locator to a `_…_locator` class attribute and use `self.find_element(*self._…_locator)` (or PyPOM `find()`). Bundles naturally with item 11.

**Effort.** S (per file, ~½ day).
**Payoff.** Locators discoverable; refactor-friendly.

---

### 13. Centralize timeouts and wait helpers in `base.py`

**Problem.** `WebDriverWait(selenium, 10)` is hardcoded throughout. Different operations (page load, file upload, validation) all share the same arbitrary 10-second budget. The `wait` fixture in `tests/conftest.py:253-258` exists but is inconsistently used (e.g. inline waits in `tests/frontend/test_addon_detail.py:324`, `tests/frontend/test_ratings.py:242, 514, 573`).

**Fix.**
1. Add timeout constants to `pages/desktop/base.py`:
   ```python
   PAGE_LOAD_TIMEOUT = 15
   ELEMENT_VISIBLE_TIMEOUT = 10
   FILE_UPLOAD_TIMEOUT = 60
   VALIDATION_TIMEOUT = 120
   ```
2. Add typed wait helpers: `wait_for_url_change`, `wait_for_loading_finished`, `wait_for_addon_validated`.
3. Replace inline `WebDriverWait(...)` with the centralized helpers.
4. Make timeouts environment-overridable (`AMO_PAGE_LOAD_TIMEOUT=20 pytest …`) so dev/stage/prod can tune independently.

**Effort.** M (3 days).
**Payoff.** Tunable per environment; bundles with item 1's sleep removal.

---

### 14. Extract duplicated boilerplate into `base.py` helpers

**Problem.** Several patterns repeat 10+ times across page objects:

**Examples.**
- Window-handling (15+ occurrences across `home.py`, `submit_addon.py`, `details.py`):
  ```python
  self.wait.until(EC.number_of_windows_to_be(2))
  new_tab = self.driver.window_handles[1]
  self.driver.switch_to.window(new_tab)
  ```
- Loading-spinner wait — identical `EC.invisibility_of_element_located((By.CLASS_NAME, "LoadingText"))` in `home.py:24`, `search.py:24`, `details.py:52`.
- `requests.head()`-based status code validation in `home.py:133, 417`.

**Fix.** Add `Base.open_in_new_tab(self, link_element) -> "Base"`, `Base.wait_for_loading_done(self)`, and `Base.assert_external_url_ok(self, url)` to `pages/desktop/base.py`. Migrate callers.

**Effort.** M (2 days plus mechanical migration).
**Payoff.** ~200 lines of duplication gone; one place to fix bugs.

---

### 15. Eliminate `@pytest.mark.serial` (213 uses)

**Problem.** 213 serial markers force whole test groups to run with `-n 1`. Most exist because tests share state (a shared FxA test account, a single addon submitted in test A and reviewed in test B, etc.). This blocks parallelization and any failure cascades through the rest of the chain.

**Examples.**
- `tests/api/test_api_addons_edit.py:28-29` — serial-marked (chained API edits).
- `tests/devhub_submissions/test_addon_submissions.py:145` — serial submission workflow.

**Fix.** Each serial test should:
1. Create its own ephemeral addon/account inline (use the API to create the prerequisite, then exercise the UI).
2. Tear down state in a function-scoped fixture (the `delete_themes` pattern in `tests/conftest.py:262-276` is the right model — extend it).
3. Once the test owns its data end-to-end, drop the marker.

This is worth doing test-by-test; even a 50% reduction makes the parallel job materially faster.

**Effort.** L (multi-quarter; one test class at a time).
**Payoff.** Real parallelism; test isolation; faster failure diagnosis.

---

### 16. Drop `pytest-rerunfailures` once flakes are fixed

**Problem.** CI runs use `--reruns 2`, which masks flakiness. Tests that fail and pass on rerun produce green builds and obscure the underlying issue. With items 1–2 and 13 done, the rerun should not be needed.

**Fix.** Remove `--reruns` from CircleCI invocations one job at a time, starting with the most stable suites (sanity, frontend). Add a quarantine marker (`@pytest.mark.flaky`) for genuinely flaky tests so they're visible rather than silently retried.

**Effort.** S (per job; coordinate with on-call for any new failure surge).
**Payoff.** Honest signal; no more "silent flaky" tests.

---

### 17. Split long test functions

**Problem.** Several tests exceed 50 lines, mixing setup, multiple assertions, and teardown into one function. Failures point to a 60-line block instead of a focused behavior.

**Examples.**
- `tests/frontend/test_addon_detail.py:826-886` — `test_click_addon_recommendations` (61 lines)
- `tests/frontend/test_addon_detail.py:438-496` — `test_more_info_external_license` (59 lines)
- `tests/frontend/test_addon_detail.py:719-773` — `test_add_to_collection_card` (55 lines)

**Fix.** Each test should assert one observable behavior. Extract setup into fixtures; split multi-aspect tests into parameterized variants.

**Effort.** M (1–2 days per file; pick the worst offenders first).
**Payoff.** Targeted failure messages; easier ownership.

---

### 18. Move hardcoded test-data slugs into variables JSON

**Problem.** Test addon slugs are inlined in test bodies. If QA renames or removes a fixture addon on stage, multiple tests fail with no central place to update them.

**Examples.**
- `tests/frontend/test_install.py:15, 54, 87, 121, 158, 197` — `"cas-current-addon-1"`, `"test_theme-auto"`, `"release_dictionary"`, `"language-עברית-hebrew-_cas-cur"`, etc.

**Fix.** Move to `stage.json` / `prod.json` / `dev.json` under a `test_addons` key; fetch via the existing `variables` fixture.

**Effort.** S (½ day).
**Payoff.** One place to update; aligns with the existing variables-driven pattern.

---

### 19. Extract repeated install-and-verify workflows into fixtures

**Problem.** The "install addon, switch to about:addons, verify state" pattern repeats verbatim 5+ times in `tests/frontend/test_install.py:31-34, 64-66, 102-105, 137-140, 174-177`.

**Fix.** Add a `verify_addon_installed` fixture (or helper) that takes an addon slug and performs the switch + assertion in one call.

**Effort.** S (½ day).
**Payoff.** Fewer copy-paste bugs; tests focus on behavior, not plumbing.

---

### 20. Add type hints to the page-object layer

**Problem.** Zero usage of type annotations in `pages/`. PyPOM page methods returning the next page object (or `None`) are ambiguous to readers and to IDE refactoring tools.

**Fix.**
1. Annotate `Region` and `Page` subclass `__init__` signatures.
2. Annotate action-method return types — `def click_login(self) -> "Login":` etc. This pairs with item 24 (chainability).
3. Add `mypy` (or `pyright`) to pre-commit, configured in non-strict mode initially; ratchet strictness over time.

**Effort.** M (incremental; can be done file-by-file; mypy config + 2 days seed).
**Payoff.** Major DX win; catches a class of refactor bugs at lint time.

---

### 21. Improve docstring coverage on page objects

**Problem.** Coverage is near zero on the largest files: `details.py` 2 docstrings / 1228 lines; `home.py` 2 / 435; `search.py` 1 / 225. Test docstring coverage is better (~64%) but inconsistent.

**Fix.** Adopt a one-line docstring convention for every public method on a page object. Where a method has non-obvious behavior (e.g. side effects, dialog handling), expand to 2–3 lines. Don't write docstrings for private helpers or trivial getters — focus where they help.

**Effort.** M (incremental; can be a "Boy Scout rule" applied during normal work).
**Payoff.** Onboarding speed.

---

<a id="p1-deps"></a>
## P1 — Tooling & dependencies

### 22. Update outdated dependencies

**Problem.** Several pinned versions are 2+ years stale and miss WebDriver protocol fixes that affect Firefox compatibility.

**Examples.**
- `requirements.txt:58` — `selenium==4.5.0` (Oct 2022). Current: 4.25+.
- `requirements.txt:48` — `pytest-html==3.1.1` (May 2022). Current: 4.x (different report format, breaking).
- `requirements.txt:42` — `pytest==7.4.4` (Aug 2023). Current: 8.x.

**Fix.** Bump in three independent PRs:
1. `selenium` → 4.25.x (verify FoxPuppet/PyFxA compatibility).
2. `pytest` 7 → 8 (review breaking changes; mostly fixture-name resolution).
3. `pytest-html` 3 → 4 (report layout differs; coordinate with anyone consuming the HTML).

**Effort.** M per bump (~1 day each, primarily testing).
**Payoff.** Bug fixes; access to newer Selenium features (BiDi).

---

### 23. Consolidate `setup.cfg` + `pytest.ini` into `pyproject.toml`

**Problem.** pytest configuration is split across two files:
- `setup.cfg:1-4` holds `addopts`, `sensitive_url`, `xfail_strict`.
- `pytest.ini:1-10` holds the marker list.

`pyproject.toml` is the modern home for all of this.

**Fix.** Add `[tool.pytest.ini_options]` to a new `pyproject.toml`:
```toml
[tool.pytest.ini_options]
addopts = "-v"
sensitive_url = 'mozilla\.(com|org)'
xfail_strict = true
testpaths = ["tests"]
filterwarnings = [
    "ignore::DeprecationWarning:pypom.*",
]
markers = [
    "serial: order-dependent tests; run with -n 1",
    # ... etc
]
```
Also adds `filterwarnings` and `testpaths` (currently missing). Delete `setup.cfg` and `pytest.ini`.

**Effort.** S (≤1 hour).
**Payoff.** One config location; matches Python community direction.

---

### 24. Migrate dependency management to a lockfile-based tool

**Problem.** `requirements.txt` is hand-pinned with no lockfile. `requirements.dev.txt` adds only `pre-commit`. Transitive dependencies are unpinned, so `pip install -r requirements.txt` can produce different trees over time.

**Fix.** Migrate to **`uv`** (fast, drop-in for `pip`/`pip-tools`):
```toml
# pyproject.toml
[project]
name = "addons-release-tests"
requires-python = ">=3.11"
dependencies = [...]
[dependency-groups]
dev = ["pre-commit"]
```
Generate `uv.lock`. CI uses `uv sync --frozen`.

Alternative: Poetry. Either is materially better than the current state.

**Effort.** M (1–2 days, including CI updates).
**Payoff.** Reproducible installs; faster CI; security audit becomes meaningful.

---

### 25. Add `pip-audit` (or `uv pip audit`) to CI

**Problem.** No automated CVE scan of dependencies. `setuptools==82.0.0`, `cryptography==43.0.1`, and others have had advisories.

**Fix.** Add a CircleCI job that runs `uv pip audit` (or `pip-audit -r requirements.txt`) and fails on any HIGH/CRITICAL CVE. Run weekly via scheduled workflow + on every PR.

**Effort.** S (½ day).
**Payoff.** Catches supply-chain issues; checks a SOC-2 box.

---

### 26. Expand pre-commit hook coverage <a id="26-expand-pre-commit-hook-coverage"></a>

**Problem.** `.pre-commit-config.yaml` registers exactly 2 hooks (`black` and `double-quote-string-fixer`). Standard hygiene hooks are absent.

**Fix.** Add:
```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.6.0
  hooks:
    - id: ruff
      args: [--fix]
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v5.0.0
  hooks:
    - id: end-of-file-fixer
    - id: trailing-whitespace
    - id: check-yaml
    - id: check-merge-conflict
    - id: detect-private-key      # would have caught the .txt cookies
    - id: check-added-large-files
      args: [--maxkb=500]          # would have caught the HTML reports
```

`ruff` replaces `pylint` + `isort` for most needs and is ~100x faster.

**Effort.** S (1 hour, plus an initial cleanup pass).
**Payoff.** Several P0 issues become structurally impossible going forward.

---

<a id="p1-ci"></a>
## P1 — CI/CD

### 27. Collapse CircleCI duplication via reusable commands

**Problem.** `.circleci/config.yml` is 691 lines. There are ~17 near-identical "install Python 3.11 → upgrade pip → install geckodriver → install Firefox" blocks across 18 jobs. Any toolchain change touches every block.

**Fix.** Use CircleCI's `commands:` feature:
```yaml
commands:
  setup_test_env:
    parameters:
      firefox_channel:
        type: enum
        enum: [release, nightly]
        default: nightly
    steps:
      - run: choco install python --version=3.11.9
      - run: py -m pip install --upgrade pip --user
      - run: py -m pip install -r requirements.txt
      - run: choco install firefox-<<parameters.firefox_channel>>
      - run: choco install selenium-gecko-driver
```
Each job becomes ~10 lines instead of ~40.

**Effort.** M (2–3 days).
**Payoff.** ~50% config-file shrink; toolchain bumps in one place.

---

### 28. Migrate Windows-only CircleCI runners to Linux <a id="28-migrate-windows-only-circleci-runners-to-linux"></a>

**Problem.** Every CircleCI job uses the Windows large executor. Windows minutes on CircleCI cost ~10× Linux minutes. If most tests don't strictly need Windows (the only Windows-specific behavior would be Windows-flavored Firefox install), the cost is wasted.

**Fix.**
1. Create a Linux variant of each job using `selenium/standalone-firefox` Docker.
2. Run both Windows + Linux for one cycle to verify parity.
3. Keep Windows only for tests that genuinely require Windows-flavored Firefox install (likely a small subset, possibly none).

**Effort.** M (3–5 days, much of it verification).
**Payoff.** Estimated 60–80% CircleCI spend reduction.

---

### 29. CI guard against artifact and cookie file leaks

**Problem.** Items 3 and 4 fix the current state, but nothing prevents a future contributor from re-adding `*.html` or `*_user.txt` to the repo.

**Fix.** Add a CI check (and pre-commit hook) that fails if a PR diff introduces a tracked `*.html` outside `docs/` or any `*_user.txt`. Trivial to implement as a 5-line shell step.

**Effort.** S (½ hour).
**Payoff.** Belt-and-suspenders for items 3–4.

---

<a id="p2-docs"></a>
## P2 — Documentation & developer experience

### 30. Add `CONTRIBUTING.md`

**Problem.** No `CONTRIBUTING.md` exists. New contributors have to grep through README + tribal knowledge to learn the marker conventions, the `.txt` cookie file dance, the `FXA_CI_HEADER` env var, and the variables-file conventions.

**Fix.** Create `CONTRIBUTING.md` covering: local setup, marker semantics, the login/create_session/clear_session chain, how to add a new test, code style, PR process.

**Effort.** S (1 day).
**Payoff.** Lower onboarding cost.

---

### 31. Update `README.md`

**Problem.**
- README assumes Windows + Docker for Windows; no macOS/Linux instructions.
- It tells users to invoke `pytest --variables stage.json --variables users.json`, but **`users.json` does not exist** in the repo — the file is referenced 3 times in the README and never produced.
- Setup section omits Firefox Nightly version requirements and the `FXA_CI_HEADER` env var.

**Examples.**
- `README.md:38, 43, 48` — every documented invocation includes a `--variables users.json` that breaks if you copy-paste.
- `README.md:13-16` — only documents Windows install paths.

**Fix.** Rewrite the "How to run locally" section with macOS/Linux/Windows tabs; remove or correct the `users.json` references; document `FXA_CI_HEADER`.

**Effort.** S (½ day).
**Payoff.** Working onboarding instructions.

---

### 32. Add an architecture overview

**Problem.** No architecture diagram. The four-layer structure (`tests/` → `pages/` → `regions/` → `api/` + `scripts/`) and the marker-driven login flow take a while to internalize from code alone. The new `CLAUDE.md` covers this for AI but not for humans.

**Fix.** Add `docs/ARCHITECTURE.md` with an ASCII or Mermaid diagram of the layers, sample flow for a typical UI test, and pointers to the key fixtures.

**Effort.** S (½ day).
**Payoff.** Onboarding; design conversations have a shared reference.

---

### 33. Document the `@login` / `@create_session` / `@clear_session` chain

**Problem.** The marker chain is the most non-obvious part of the codebase. `@login(user)` writes a `<user>.txt` cookie, `@create_session(user)` reads it, `@clear_session` deletes it. This is implemented in `tests/conftest.py:170-203` but documented nowhere.

**Fix.** Add a section to `CONTRIBUTING.md` (or `docs/ARCHITECTURE.md`) explaining the lifecycle, when to use each marker, and how the `.txt` files relate. Pairs naturally with items 30 and 32.

**Effort.** S (folded into 30/32).
**Payoff.** Removes the most common onboarding stumbling block.

---

<a id="p2-arch"></a>
## P2 — Architecture polish & strategic modernization

### 34. Flatten deeply nested PyPOM regions

**Problem.** Some regions nest 5+ levels deep (e.g. `pages/desktop/frontend/home.py:380-435` — `SecondaryHeroModules` is 3 levels nested inside Home). Deep nesting makes locator scoping confusing and the navigation `Home().section.subsection.item` chains brittle.

**Fix.** Promote frequently-accessed sub-regions to siblings of the page; reserve nesting for genuine DOM containment.

**Effort.** M (per page; opportunistic).
**Payoff.** Clearer call sites.

---

### 35. Standardize action-method return types

**Problem.** Action methods return either the next page or `None` inconsistently. `pages/desktop/frontend/details.py:91 install()` returns nothing; `pages/desktop/frontend/home.py:120 click()` returns `Detail`. This breaks fluent chaining.

**Fix.** Convention: every action method returns `self` if it stays on the same page, or the next page object otherwise. Pair with type hints (item 20) so violations become type errors.

**Effort.** M (incremental).
**Payoff.** Fluent test-writing style; type-checker enforcement.

---

### 36. Consider Allure (or pytest-html v4) for richer reports

**Problem.** Current `pytest-html` 3.1.1 reports are functional but limited (no step grouping, weak attachment support, hard to share). With Linux runners (item 28) and a richer reporter, debugging shared CI failures becomes materially easier.

**Fix.** Spike `pytest-allure-adaptor` against one test suite for a week; compare against a `pytest-html` v4 upgrade. Pick whichever fits better.

**Effort.** M (spike: 2 days; rollout: 3 days).
**Payoff.** Faster failure triage; better PM visibility into what tests cover.

---

### 37. Add GitHub Actions as a parallel/pre-merge gate

**Problem.** All CI is in CircleCI. PR-time fast feedback (lint, type-check, single sanity test) could happen on GitHub Actions for free, with CircleCI reserved for the heavy multi-environment runs.

**Fix.** Add `.github/workflows/quick-check.yml` that runs ruff + mypy + a 5-test sanity smoke on every PR. Keep CircleCI for the full matrix.

**Effort.** M (2 days).
**Payoff.** Sub-minute PR feedback on the cheap stuff; reduces CircleCI load.

---

<a id="appendix"></a>
## Appendix: metrics snapshot

*All measurements taken from the working tree on 2026-04-28.*

| Metric | Value |
|---|---:|
| Total `time.sleep()` calls (`pages/` + `tests/`) | 85 |
| Largest single sleep | `time.sleep(500)` (login.py:214) |
| `@pytest.mark.serial` decorators | 213 |
| `@pytest.mark.skip` decorators | 28 |
| `@pytest.mark.xfail` decorators | 1 |
| `By.XPATH` locator usages (`pages/`) | 88 |
| `By.CSS_SELECTOR` locator usages (`pages/`) | 533 |
| Largest page-object file | `details.py` (1228 lines) |
| Page-object files >500 lines | 6 |
| Page-object files >750 lines | 4 |
| Type-hint coverage (`pages/`) | 0% |
| Docstrings in `details.py` | 2 / 1228 LOC |
| Bare `assert`s in `test_install.py` | 17 / 17 (0 messaged) |
| `.gitignore` line count | 4 |
| Tracked HTML test reports at root | 11 |
| Tracked session-cookie `.txt` files at root | 7 |
| `.DS_Store` tracked | yes |
| CircleCI config size | 691 lines |
| CircleCI jobs | 18 |
| Estimated duplicated install blocks in CI | ~17 |
| Dockerfile base image | `windows:2004` (EOL Dec 2021) |
| Dockerfile-pinned Selenium version | 3.141.59 (2018) |
| Dockerfile-pinned Firefox version | 66.0.3 (April 2019) |
| `selenium` (requirements.txt) | 4.5.0 (Oct 2022) |
| `pytest` (requirements.txt) | 7.4.4 (Aug 2023) |
| `pytest-html` (requirements.txt) | 3.1.1 (May 2022) |
| pre-commit `black` rev | `stable` (deprecated) |

---

*This audit is a snapshot. Regenerate the metrics table after each batch of fixes to track progress.*
