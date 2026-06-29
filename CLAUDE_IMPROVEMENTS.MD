# CLAUDE_IMPROVEMENTS.md

Proposed improvements for `addons-release-tests`, derived from the same repository
analysis that produced `CLAUDE.md`. Each item states **what** to change, **why** it
matters, and a rough **effort** estimate. Nothing here has been applied — this is a backlog,
ordered roughly by value-to-effort.

Legend: **Effort** = S (hours) · M (a day) · L (multi-day).

---

## 1. Correctness & consistency (highest value)

### 1.1 Register all pytest markers — S
Tests use `@pytest.mark.search` and `@pytest.mark.webext`, but `pytest.ini` only registers
`serial, sanity, prod_only, firefox_release, login, create_session, clear_session,
nondestructive`. Unregistered markers raise `PytestUnknownMarkWarning` and silently no-op in
`-m` selection.
- **Fix:** add every marker in use to `pytest.ini`; consider `--strict-markers` in `addopts`
  so a typo'd marker fails fast instead of selecting nothing.
- **Why:** marker selection drives which CI job runs a test; a silently-ignored marker means a
  test runs in the wrong job (or every job).

### 1.2 Make string-quote style consistent and enforce it — S→M
The codebase mixes single quotes (older `scripts/`, `regions/`) and double quotes (newer
`tests/conftest.py`, `pages/desktop/base.py`). The pre-commit `double-quote-string-fixer`
hook *prefers single quotes* while the newer code clearly standardised on double.
- **Fix:** pick one (the newer code leans double-quote), drop the conflicting hook or switch
  to a formatter that owns quotes (e.g. drop `--skip-string-normalization` so black
  normalises), then reformat once in a dedicated commit.
- **Why:** the current setup means pre-commit and the code actively disagree; contributors
  (and AI) get whipsawed.

### 1.3 Pin the pre-commit `black` revision — S
`.pre-commit-config.yaml` uses `rev: stable`, which is deprecated and non-reproducible.
`pre-commit-hooks` is pinned to `v2.5.0` (very old).
- **Fix:** pin `black` to a concrete tag and bump `pre-commit-hooks`.
- **Why:** reproducible formatting; `rev: stable` can break without warning.

### 1.4 Wire (or remove) pylint/isort — S
`pylint` and `isort` are in `requirements.txt` but nothing runs them and there's no config.
- **Fix:** either add `isort` + `pylint` to `.pre-commit-config.yaml`/CI with a checked-in
  config, or move them out of the runtime requirements file.
- **Why:** ambiguous tooling invites inconsistent local setups; an AI can't tell if import
  order is enforced.

---

## 2. Test reliability

### 2.1 Reduce reliance on `--reruns 2` as a flakiness band-aid — M (ongoing)
CI sets `PYTEST_ADDOPTS: ... --reruns 2` everywhere. Reruns hide flakiness rather than fixing
it and triple the cost of a genuinely failing test.
- **Fix:** track which tests actually consume reruns (pytest-rerunfailures reports this),
  then fix the underlying waits. Audit the handful of `time.sleep(...)` calls (e.g.
  `tests/frontend/test_search.py` autocomplete debounce) and replace with explicit
  `expected_conditions` where feasible.
- **Why:** rerun-masked flakiness erodes trust in red/green signal before a prod release.

### 2.2 Centralise the stale-element + hover dropdown pattern — M
`pages/desktop/base.py` repeats `WebDriverWait(self.driver, 30,
ignored_exceptions=StaleElementReferenceException)` and the ActionChains
move→pause→click dropdown dance in `click_logout`, `click_user_menu_links`, `more_menu`.
- **Fix:** extract a `Base.hover_and_click(trigger_locator, target_locator)` helper and a
  `stale_safe_wait(timeout)` helper.
- **Why:** the duplication is the most copy-pasted logic in the repo and a frequent flake
  source; one fix should fix all callers.

### 2.3 Standardise the `wait` fixture — S
`tests/conftest.py:wait` builds `WebDriverWait(selenium, 10, ...)` but references the
*module-level* `selenium` name, not the fixture — it does not receive the driver argument.
This looks like a latent bug; tests that depend on `wait` may be getting an unexpected object.
- **Fix:** make it `def wait(selenium): return WebDriverWait(selenium, 10,
  ignored_exceptions=StaleElementReferenceException)`.
- **Why:** silent misbehaviour; verify current usages still pass after the fix.

---

## 3. Documentation & onboarding

### 3.1 Reconcile the README with the code — S
`README.md` documents mobile+desktop resolutions and a `users.json`, but the `selenium`
fixture only parametrises **Desktop (1920x1080)** and auth flows through marker-driven
`<user>.txt` session files.
- **Fix:** update README to match current reality (or restore mobile parametrisation if it's
  intended), and document the `login`/`create_session`/`clear_session` auth model.
- **Why:** the two most-read docs disagree with the code; this is the top source of wrong
  assumptions.

### 3.2 Document required environment variables — S
`CUSTOM_USER_AGENT`, `MOZ_HEADLESS`, and the FxA/CI header (named indirectly via
`variables["FXA_CI_HEADER"]`) are only discoverable by reading `conftest.py`.
- **Fix:** add a `.env.example` and a short "Environment variables" section to the README.
- **Why:** the WAF-bypass setup is opaque to newcomers; a missing var produces confusing
  captcha failures.

### 3.3 Add a fixtures/markers quick-reference near the tests — S
- **Fix:** a short `tests/README.md` table mapping each marker and shared fixture to its
  purpose and which CI job consumes it.
- **Why:** co-located docs are found more reliably than a single root file; speeds up authoring.

---

## 4. Repository hygiene

### 4.1 Stop committing generated HTML reports — S
The root holds many large `*-results.html` files (several are multi-MB; e.g.
`webext-release_prod-results.html` is ~18 MB). These are pytest-html artifacts.
- **Fix:** add `*-results.html` to `.gitignore`, remove the tracked copies, and rely on
  CircleCI `store_artifacts` (already configured) for report retention.
- **Why:** these bloat the repo and clones, and create noisy diffs; CI already stores them.

### 4.2 Don't track session/secret-ish scratch files — S
`<user>.txt` session-cookie files and a stray `keychain_dump.json` appear in the working tree.
Session cookies are short-lived credentials.
- **Fix:** ensure all `*_user.txt` / `<user>.txt` and `keychain_dump.json` are gitignored and
  not committed; confirm none are in history (rotate/scrub if so).
- **Why:** avoids leaking live session tokens.

### 4.3 Refresh or remove the Dockerfile — M
`Dockerfile` targets Windows containers with Selenium 3.141, GeckoDriver 0.26.0, and Firefox
66 — none of which match the current Selenium 4 / Nightly setup or the CircleCI executors.
- **Fix:** either update it to a working Selenium 4 + Nightly image or delete it and document
  the `--driver Remote` selenium-standalone path another way.
- **Why:** the documented local Docker path is broken; it misleads contributors.

---

## 5. CI / automation

### 5.1 Run lint/format in CI, not just locally — S
Pre-commit hooks only run on machines where contributors installed them. CircleCI runs no
formatting/lint gate.
- **Fix:** add a fast `lint` job (`pre-commit run --all-files`) to `commit_workflow`.
- **Why:** keeps style consistent regardless of local setup; cheap and fast.

### 5.2 Reduce duplication in `.circleci/config.yml` — M
The Firefox-Nightly-via-APT install block is copy-pasted across nearly every job (~10×).
- **Fix:** extract a reusable **command** (CircleCI `commands:`) or a custom executor that
  pre-installs Nightly, and reference it.
- **Why:** a one-line change to the install steps currently means editing ~10 blocks; drift is
  likely (one job already pins Python 3.11 while others use 3.14).

### 5.3 Align Python versions — S
Most jobs use `cimg/python:3.14-browsers`; the webext release job invokes `py -3.11`. The
coverage job installs Python 3.14 on Windows.
- **Fix:** standardise on one Python minor version across jobs unless 3.11 is deliberate
  (document why if so).
- **Why:** version skew causes "works in one job, fails in another" surprises.

---

## 6. Structure & extensibility (longer-term)

### 6.1 Add a `requirements` constraint/lock strategy — M
`requirements.txt` is fully pinned (good), but with daily Dependabot PRs limited to one at a
time there's no separation of direct vs. transitive pins.
- **Fix:** consider `pip-tools` (`requirements.in` → compiled `requirements.txt`) so direct
  deps are obvious and upgrades are reviewable.
- **Why:** clarifies intent and makes Dependabot diffs easier to reason about.

### 6.2 Type hints + docstring consistency on helpers — M
`scripts/` and `api/` helpers are well-documented prose but untyped. Adding signatures
(`def get_random_string(length: int) -> str:`) would help editors and AI.
- **Why:** cheap correctness aid; the helper surface is small and stable.

### 6.3 Consider a shared assertion-message helper — S
The `assert x == y, f"Actual ... was {x}"` pattern is everywhere and hand-written each time.
- **Fix:** optional small helpers for the most common shapes (status code, element text).
- **Why:** consistency and less boilerplate; keep it lightweight so tests stay readable.

---

## Suggested order of attack

1. **Quick wins (S):** 1.1, 1.3, 3.1, 4.1, 4.2, 5.1 — low risk, immediate clarity/safety.
2. **Reliability (M):** 2.1, 2.2, 2.3 — the flakiness work that protects release confidence.
3. **Consistency cleanup (S→M):** 1.2, 1.4, 5.2, 5.3.
4. **Longer-term (M):** 4.3, 6.x as capacity allows.

> Note: items in §2.3 and §4.2 may surface latent bugs/secrets — verify behaviour and scrub
> history carefully rather than applying blindly.
