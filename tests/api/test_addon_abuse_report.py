import json
import time

import pytest
import requests

from api import payloads, api_helpers, responses
from pages.desktop.frontend.home import Home
from scripts import reusables

# endpoints used in the post abuse report tests
_post_abuse_report = "/api/v5/abuse/report/addon/"


@pytest.mark.login("api_user")
def test_abuse_report_unauthenticated_post(base_url, selenium):
    payload = payloads.abuse_report_full_body
    create_abuse_report = requests.post(
        url=f"{base_url}{_post_abuse_report}",
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps(payload)
    )
    assert (
            create_abuse_report.status_code == 201
    ), f"Actual response: {create_abuse_report.status_code}, {create_abuse_report.text}"

    assert (
            create_abuse_report.json() == responses.abuse_report_unauthenticated_response
    ), f"Actual response: {create_abuse_report.json()}"


@pytest.mark.create_session("api_user")
def test_abuse_report_authenticated(base_url, selenium, session_auth):
    payload = payloads.abuse_report_full_body
    create_abuse_report = requests.post(
        url=f"{base_url}{_post_abuse_report}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Session {session_auth}"
        },
        data=json.dumps(payload)
    )
    assert (
            create_abuse_report.status_code == 201
    ), f"Actual response: {create_abuse_report.status_code}, {create_abuse_report.text}"

    assert (
            create_abuse_report.json() == responses.abuse_report_authenticated_response
    ), f"Actual response: {create_abuse_report.json()}"


def test_abuse_report_minimal_details(base_url, selenium):
    payload = {
        "addon": "{463b483d-6150-43c9-9b52-a3d08d5ecd3a}",
        "message": "test from the API,both"
    }
    create_abuse_report = requests.post(
        url=f"{base_url}{_post_abuse_report}",
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps(payload)
    )
    assert (
            create_abuse_report.status_code == 201
    ), f"Actual response: {create_abuse_report.status_code}, {create_abuse_report.text}";
    assert (
            create_abuse_report.json() == responses.abuse_report_minimal_details
    ), f"Actual response: {create_abuse_report.json()}"


@pytest.mark.parametrize(
    "addon_install_method",
    [
        "link",
        "random_text"
    ],
    ids=[
        'Accepted value: link',
        'Unsupported value: random_text'
    ]
)
def test_addon_install_method_parameter(base_url, selenium, addon_install_method):
    payload = payloads.abuse_report_body(f"{addon_install_method}", "amo", "settings", "signed", "menu", "amo")
    create_abuse_report = requests.post(
        url=f"{base_url}{_post_abuse_report}",
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps(payload)
    )
    assert (
            create_abuse_report.status_code == 201
    ), f"Actual response: {create_abuse_report.status_code}, {create_abuse_report.text}";
    assert (
            create_abuse_report.json()["addon_install_method"] == addon_install_method
    ), f"Actual response: {create_abuse_report.json()}"


@pytest.mark.parametrize(
    "addon_install_source",
    [
        "amo",
        "random_text"
    ],
    ids=[
        'Accepted value: amo',
        'Unsupported value: random_text'
    ]
)
def test_addon_install_source_parameter(base_url, selenium, addon_install_source):
    payload = payloads.abuse_report_body("link", f"{addon_install_source}", "settings", "signed", "menu", "amo")
    create_abuse_report = requests.post(
        url=f"{base_url}{_post_abuse_report}",
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps(payload)
    )
    assert (
            create_abuse_report.status_code == 201
    ), f"Actual response: {create_abuse_report.status_code}, {create_abuse_report.text}";
    assert (
            create_abuse_report.json()["addon_install_method"] == addon_install_source
    ), f"Actual response: {create_abuse_report.json()}"


@pytest.mark.parametrize(
    "reason",
    [
        "damage",
        "random_text"
    ],
    ids=[
        'Accepted value: damage',
        'Unsupported value: random_text'
    ]
)
def test_reason_parameter(base_url, selenium, reason):
    payload = payloads.abuse_report_body("link", "amo", f"{reason}", "signed", "menu", "amo")
    create_abuse_report = requests.post(
        url=f"{base_url}{_post_abuse_report}",
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps(payload)
    )
    assert (
            create_abuse_report.status_code == 201
    ), f"Actual response: {create_abuse_report.status_code}, {create_abuse_report.text}";
    assert (
            create_abuse_report.json()["addon_install_method"] == reason
    ), f"Actual response: {create_abuse_report.json()}"


@pytest.mark.parametrize(
    "addon_signature",
    [
        "curated_and_partner",
        "random_text"
    ],
    ids=[
        'Accepted value: curated_and_partner',
        'Unsupported value: random_text'
    ]
)
def test_addon_signature_parameter(base_url, selenium, addon_signature):
    payload = payloads.abuse_report_body("installtrigger", "about_preferences", "broken", f"{addon_signature}",
                                         "uninstall", "addon")
    create_abuse_report = requests.post(
        url=f"{base_url}{_post_abuse_report}",
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps(payload)
    )
    assert (
            create_abuse_report.status_code == 201
    ), f"Actual response: {create_abuse_report.status_code}, {create_abuse_report.text}";
    assert (
            create_abuse_report.json()["addon_install_method"] == addon_signature
    ), f"Actual response: {create_abuse_report.json()}"


@pytest.mark.parametrize(
    "report_entry_point",
    [
        "unified_context_menu",
        "random_text"
    ],
    ids=[
        'Accepted value: unified_context_menu',
        'Unsupported value: random_text'
    ]
)
def test_report_entry_point_parameter(base_url, selenium, report_entry_point):
    payload = payloads.abuse_report_body("drag_and_drop", "app_profile", "policy", "preliminary",
                                         f"{report_entry_point}", "addon")
    create_abuse_report = requests.post(
        url=f"{base_url}{_post_abuse_report}",
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps(payload)
    )
    assert (
            create_abuse_report.status_code == 201
    ), f"Actual response: {create_abuse_report.status_code}, {create_abuse_report.text}";
    assert (
            create_abuse_report.json()["addon_install_method"] == report_entry_point
    ), f"Actual response: {create_abuse_report.json()}"


@pytest.mark.parametrize(
    "location",
    [
        "both",
        "random_text"
    ],
    ids=[
        'Accepted value: both',
        'Unsupported value: random_text'
    ]
)
def test_location_parameter(base_url, selenium, location):
    payload = payloads.abuse_report_body("link", "amo", "settings", "signed", "menu", f"{location}")
    create_abuse_report = requests.post(
        url=f"{base_url}{_post_abuse_report}",
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps(payload)
    )
    assert (
            create_abuse_report.status_code == 201
    ), f"Actual response: {create_abuse_report.status_code}, {create_abuse_report.text}";
    assert (
            create_abuse_report.json()["addon_install_method"] == location
    ), f"Actual response: {create_abuse_report.json()}"
