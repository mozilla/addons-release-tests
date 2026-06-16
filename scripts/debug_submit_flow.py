"""Debug script: walk through the AMO listed addon submission flow on dev,
log URL at each step, and capture source/details page structure."""
import json
import os
import sys
import time
import zipfile
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://addons-dev.allizom.org"
REPO = Path("/Users/alexandru.schek/addons-release-tests")
SESSION_COOKIE = (REPO / "submissions_user.txt").read_text().strip()
LISTED_ADDON = str(REPO / "sample-addons" / "listed-addon.zip")
HEADER_VALUE = os.environ["FXA_CI_HEADER_DEV"]


def build_waf_bypass_addon(out_dir: Path) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "manifest_version": 2,
        "name": "WAF Bypass Header",
        "version": "1.0",
        "permissions": ["webRequest", "webRequestBlocking", "<all_urls>"],
        "background": {"scripts": ["background.js"]},
    }
    bg = f"""
browser.webRequest.onBeforeSendHeaders.addListener(
  function(details) {{
    details.requestHeaders.push({{name: "fxa-ci", value: "{HEADER_VALUE}"}});
    return {{ requestHeaders: details.requestHeaders }};
  }},
  {{ urls: ["<all_urls>"] }},
  ["blocking", "requestHeaders"]
);
"""
    (out_dir / "manifest.json").write_text(json.dumps(manifest))
    (out_dir / "background.js").write_text(bg)
    zpath = out_dir / "waf_bypass_addon.zip"
    with zipfile.ZipFile(zpath, "w") as z:
        z.write(out_dir / "manifest.json", "manifest.json")
        z.write(out_dir / "background.js", "background.js")
    return str(zpath)


def log(msg):
    print(f"[debug] {msg}", flush=True)


def dump(driver, label):
    log(f"--- {label} ---")
    log(f"URL: {driver.current_url}")
    log(f"TITLE: {driver.title}")
    try:
        h1 = driver.find_element(By.CSS_SELECTOR, "h1, h2, h3").text[:200]
        log(f"HEADER: {h1!r}")
    except Exception:
        pass


def main():
    waf_zip = build_waf_bypass_addon(Path("/tmp/debug_waf_bypass"))
    opts = Options()
    opts.set_preference("extensions.install.requireBuiltInCerts", False)
    opts.set_preference("xpinstall.signatures.required", False)
    opts.set_preference("xpinstall.signatures.dev-root", True)
    opts.set_preference("extensions.webapi.testing", True)
    opts.add_argument("-foreground")
    opts.add_argument("-headless")

    driver = webdriver.Firefox(options=opts)
    driver.set_window_size(1920, 1080)
    wait = WebDriverWait(driver, 30)

    try:
        driver.install_addon(waf_zip, temporary=True)
        # Set session cookie
        driver.get(BASE_URL)
        driver.add_cookie({"name": "sessionid", "value": SESSION_COOKIE})
        log(f"Set sessionid cookie ({len(SESSION_COOKIE)} chars)")

        # Visit submit agreement page
        driver.get(f"{BASE_URL}/developers/addon/submit/agreement")
        time.sleep(2)
        dump(driver, "After /submit/agreement")

        # Check if redirected to login; if so, abort
        if "accounts" in driver.current_url and "addons" not in driver.current_url:
            log("ERROR: redirected to login - session cookie invalid")
            return

        # If on agreement page, accept it
        if "/submit/agreement" in driver.current_url:
            try:
                # Accept distribution agreement
                for cb_id in ["id_distribution_agreement", "id_review_policy"]:
                    try:
                        cb = driver.find_element(By.ID, cb_id)
                        if not cb.is_selected():
                            cb.click()
                            log(f"Checked {cb_id}")
                    except Exception as e:
                        log(f"no {cb_id}: {e}")
                # Recaptcha may be present - try the continue button
                btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                btn.click()
                time.sleep(3)
                dump(driver, "After accepting agreement")
            except Exception as e:
                log(f"agreement step issue: {e}")

        # Should be on /submit/distribution; select listed
        if "/submit/distribution" in driver.current_url:
            try:
                driver.find_element(By.ID, "id_channel_0").click()  # listed = 0 likely
                log("Selected listed channel (id_channel_0)")
            except Exception as e:
                log(f"channel select issue: {e}")
            try:
                # Continue button
                driver.find_element(By.CSS_SELECTOR, "button.submit-buttons, button[type='submit']").click()
            except Exception:
                pass
            time.sleep(3)
            dump(driver, "After distribution continue")

        # Now we should be on /submit/upload-listed
        log(f"Now at {driver.current_url}")
        # Upload the addon zip
        try:
            file_input = driver.find_element(By.ID, "upload-addon")
            file_input.send_keys(LISTED_ADDON)
            log(f"Sent file: {LISTED_ADDON}")
        except Exception as e:
            log(f"upload input issue: {e}")
            # Print all input[type=file]
            inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            for i in inputs:
                log(f"  file input: id={i.get_attribute('id')} name={i.get_attribute('name')}")

        # Wait for validation success
        try:
            WebDriverWait(driver, 90).until(
                EC.visibility_of_element_located((By.ID, "upload-status-results"))
            )
            log("upload-status-results visible")
        except Exception as e:
            log(f"validation wait issue: {e}")

        time.sleep(5)
        dump(driver, "After upload + validation")

        # Check Android compat checkbox if present
        try:
            android_cb = driver.find_element(By.CSS_SELECTOR, "input[name='compatible_apps'][value='61']")
            if not android_cb.is_selected():
                android_cb.click()
                log("Clicked Android compat")
                time.sleep(2)
                # Try the "Yes, I've tested" confirmation button
                yes_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Yes')]")
                log(f"yes-button candidates: {len(yes_buttons)}")
                for yb in yes_buttons:
                    try:
                        if yb.is_displayed():
                            log(f"clicking yes: {yb.text!r}")
                            yb.click()
                            time.sleep(1)
                            break
                    except Exception:
                        pass
        except Exception as e:
            log(f"android compat skip: {e}")

        # Click the continue/submit button on upload page
        log("Looking for submit-upload button...")
        candidates = driver.find_elements(By.CSS_SELECTOR, "button.upload-file-submit, button#submit-upload-file-finish, button[type='submit']")
        for c in candidates:
            log(f"  candidate: id={c.get_attribute('id')} text={c.text!r} class={c.get_attribute('class')}")
        try:
            btn = driver.find_element(By.ID, "submit-upload-file-finish")
            log(f"submit-upload-file-finish: disabled={btn.get_attribute('disabled')} class={btn.get_attribute('class')}")
            # Wait for button to be enabled
            for _ in range(20):
                if not btn.get_attribute("disabled"):
                    break
                time.sleep(0.5)
            log(f"after wait: disabled={btn.get_attribute('disabled')}")
            driver.execute_script("arguments[0].scrollIntoView();", btn)
            btn.click()
            log("Clicked submit-upload-file-finish")
        except Exception as e:
            log(f"continue button issue: {e}")

        time.sleep(5)
        dump(driver, "AFTER clicking continue from upload page")

        # Inspect page: is it /submit/source or /submit/details?
        url = driver.current_url
        log(f"## KEY URL AFTER UPLOAD CONTINUE: {url}")

        if "/submit/source" in url:
            log("OK - landed on source page")
            for sel in [(By.ID, "id_has_source_0"), (By.ID, "id_has_source_1"), (By.ID, "id_source")]:
                try:
                    el = driver.find_element(*sel)
                    log(f"  found {sel}: tag={el.tag_name} type={el.get_attribute('type')}")
                except Exception:
                    log(f"  MISSING {sel}")
        elif "/submit/details" in url:
            log("PROBLEM - skipped source page, on details")
            # Dump key form fields
            for sel in [
                "input#id_name_0", "textarea#id_summary_0", "textarea#id_description_0",
                "input#id_is_experimental", "input#id_requires_payment",
                "input#id_support_email", "input#id_support_url_0",
                "select#id_license-builtin", "input[name='license-builtin']",
                "textarea#id_privacy_policy_0", "textarea#id_approval_notes",
                "button[type='submit']",
            ]:
                els = driver.find_elements(By.CSS_SELECTOR, sel)
                log(f"  selector {sel}: count={len(els)}")
            # Find all form fields more broadly
            page_h2 = [e.text for e in driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3")][:8]
            log(f"  headers: {page_h2}")
            # Save HTML snippet
            html = driver.page_source
            out = Path("/tmp/dev_submit_details.html")
            out.write_text(html)
            log(f"  details HTML saved to {out} ({len(html)} chars)")
        else:
            log(f"UNEXPECTED URL: {url}")

        # If we are on /submit/details, fill minimal then submit to see what comes next
        if "/submit/details" in driver.current_url:
            log("Attempting minimal details submit to discover post-submit URL...")
            try:
                # Use the trans-init pattern: click trans-* container, then send keys to the visible _0 input
                def set_trans(field_name, value):
                    try:
                        cont = driver.find_element(By.ID, f"trans-{field_name}")
                        driver.execute_script("arguments[0].scrollIntoView();", cont)
                        cont.click()
                        time.sleep(0.5)
                    except Exception as e:
                        log(f"  trans-{field_name} click err: {e}")
                    try:
                        el = driver.find_element(By.ID, f"id_{field_name}_0")
                        el.clear()
                        el.send_keys(value)
                        log(f"  set id_{field_name}_0={value!r}")
                    except Exception as e:
                        log(f"  id_{field_name}_0 err: {e}")

                # Set a unique slug via JS (avoid edit_slug toggle issues)
                try:
                    new_slug = f"debug-addon-{int(time.time())}"
                    driver.execute_script(
                        "document.getElementById('id_slug').value = arguments[0];", new_slug
                    )
                    log(f"set id_slug={new_slug}")
                except Exception as e:
                    log(f"slug err: {e}")
                set_trans("summary", "Debug summary text")
                set_trans("description", "Debug description text for AMO submission flow.")
                # Support email is non-translated
                try:
                    em = driver.find_element(By.ID, "id_support_email")
                    em.clear()
                    em.send_keys("debug@example.com")
                    log("set id_support_email")
                except Exception as e:
                    log(f"email err: {e}")
                # Select first license
                lic_inputs = driver.find_elements(By.CSS_SELECTOR, "input[name='license-builtin']")
                if lic_inputs:
                    lic_inputs[0].click()
                    log(f"Selected license[0]: id={lic_inputs[0].get_attribute('id')}")
                # Category
                cat_inputs = driver.find_elements(By.CSS_SELECTOR, "input[name='categories']")
                if cat_inputs:
                    cat_inputs[0].click()
                    log(f"Selected category[0]")
                # No need to set privacy policy (it's optional). Skip.
                # Find the "Submit Version" button - it's the first child of .submission-buttons
                submit_btn = driver.find_element(By.CSS_SELECTOR, ".submission-buttons button:nth-child(1)")
                log(f"Submit button text={submit_btn.text!r} id={submit_btn.get_attribute('id')}")
                driver.execute_script("arguments[0].scrollIntoView();", submit_btn)
                submit_btn.click()
                time.sleep(8)
                dump(driver, "AFTER details submit")
                log(f"## KEY URL AFTER DETAILS SUBMIT: {driver.current_url}")
                # Dump headers and key text
                headers = [e.text for e in driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3")][:8]
                log(f"  post-submit headers: {headers}")
                # Save html
                out2 = Path("/tmp/dev_post_submit.html")
                out2.write_text(driver.page_source)
                log(f"  post-submit HTML saved to {out2}")
                # Find prominent text
                texts = [e.text[:160] for e in driver.find_elements(By.CSS_SELECTOR, ".submission-process, .addon-submission-process, .island")[:3]]
                log(f"  prominent text: {texts}")

                # If we landed on source-listed, walk through it
                if "/submit/source" in driver.current_url:
                    log("=== NEW source page after details ===")
                    for sel in [(By.ID, "id_has_source_0"), (By.ID, "id_has_source_1"), (By.ID, "id_source"),
                                (By.ID, "option_yes_source"), (By.ID, "option_no_source"),
                                (By.ID, "submit-source")]:
                        try:
                            el = driver.find_element(*sel)
                            log(f"  found {sel}: tag={el.tag_name} type={el.get_attribute('type')} visible={el.is_displayed()}")
                        except Exception:
                            log(f"  MISSING {sel}")
                    # Click "No" to skip source
                    no_radio = driver.find_element(By.ID, "id_has_source_1")
                    driver.execute_script("arguments[0].click();", no_radio)
                    log(f"clicked No source ({no_radio.get_attribute('id')})")
                    time.sleep(1)
                    src_submit = driver.find_element(By.CSS_SELECTOR, ".submission-buttons button:nth-child(1)")
                    log(f"source submit button text={src_submit.text!r}")
                    driver.execute_script("arguments[0].click();", src_submit)
                    time.sleep(6)
                    dump(driver, "AFTER source-listed submit")
                    log(f"## FINAL URL: {driver.current_url}")
                    headers = [e.text for e in driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3")][:8]
                    log(f"  final headers: {headers}")
                    confs = driver.find_elements(By.CSS_SELECTOR, ".addon-submission-process p")
                    for p in confs[:5]:
                        log(f"  conf-p: {p.text[:200]!r}")
                    out3 = Path("/tmp/dev_final.html")
                    out3.write_text(driver.page_source)
                    log(f"  final HTML saved to {out3}")
            except Exception as e:
                log(f"details submit issue: {e}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
