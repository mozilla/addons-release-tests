import json

import pytest
import requests

from api import payloads, api_helpers, responses


# endpoints used in the post abuse report tests
_post_abuse_report = "/api/v5/abuse/report/addon/"

@pytest.mark.skip(reason="Skipped for the moment due to throttle in place, to be removed with next pr")
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


@pytest.mark.login("api_user")
def test_abuse_report_authenticated(base_url, selenium):
    payload = payloads.abuse_report_full_body
    session_cookie = selenium.get_cookie("sessionid")
    create_abuse_report = requests.post(
        url=f"{base_url}{_post_abuse_report}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f'Session {session_cookie["value"]}'
        },
        data=json.dumps(payload)
    )
    assert (
            create_abuse_report.status_code == 201
    ), f"Actual response: {create_abuse_report.status_code}, {create_abuse_report.text}"

    assert (
            create_abuse_report.json() == responses.abuse_report_authenticated_response
    ), f"Actual response: {create_abuse_report.json()}"

@pytest.mark.create_session("api_user")
def test_abuse_report_minimal_details(base_url, selenium, session_auth):
    payload = {
        "addon": "{463b483d-6150-43c9-9b52-a3d08d5ecd3a}",
        "message": "test from the API,both"
    }
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
@pytest.mark.create_session("api_user")
def test_addon_install_method_parameter(base_url, selenium, session_auth, addon_install_method):
    payload = payloads.abuse_report_body(f"{addon_install_method}", "amo", "settings", "signed", "menu", "amo")
    create_abuse_report = requests.post(
        url=f"{base_url}{_post_abuse_report}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Session {session_auth}"
        },
        data=json.dumps(payload)
    )
    if addon_install_method == "random_text":
        assert (
                create_abuse_report.status_code == 201
        ), f"Actual response: {create_abuse_report.status_code}, {create_abuse_report.text}";
        assert (
                create_abuse_report.json()["addon_install_method"] == "other"
        ), f"Actual response: {create_abuse_report.json()}"
    else:
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
@pytest.mark.create_session("api_user")
def test_addon_install_source_parameter(base_url, selenium, session_auth, addon_install_source):
    payload = payloads.abuse_report_body("link", f"{addon_install_source}", "settings", "signed", "menu", "amo")
    create_abuse_report = requests.post(
        url=f"{base_url}{_post_abuse_report}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Session {session_auth}"
        },
        data=json.dumps(payload)
    )
    if addon_install_source == "random_text":
        assert (
                create_abuse_report.status_code == 201
        ), f"Actual response: {create_abuse_report.status_code}, {create_abuse_report.text}";
        assert (
                create_abuse_report.json()["addon_install_source"] == "other"
        ), f"Actual response: {create_abuse_report.json()}"
    else:
        assert (
                create_abuse_report.status_code == 201
        ), f"Actual response: {create_abuse_report.status_code}, {create_abuse_report.text}";
        assert (
                create_abuse_report.json()["addon_install_source"] == addon_install_source
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
@pytest.mark.create_session("api_user")
def test_reason_parameter(base_url, selenium, session_auth, reason):
    payload = payloads.abuse_report_body("link", "amo", f"{reason}", "signed", "menu", "amo")
    create_abuse_report = requests.post(
        url=f"{base_url}{_post_abuse_report}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Session {session_auth}"
        },
        data=json.dumps(payload)
    )
    if reason == "random_text":
        assert (
                create_abuse_report.status_code == 400
        ), f"Actual response: {create_abuse_report.status_code}, {create_abuse_report.text}";
        assert (
                create_abuse_report.json() == {'reason': ['"random_text" is not a valid choice.']}
        ), f"Actual response: {create_abuse_report.json()}"
    else:
        assert (
                create_abuse_report.status_code == 201
        ), f"Actual response: {create_abuse_report.status_code}, {create_abuse_report.text}";
        assert (
                create_abuse_report.json()["reason"] == reason
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
@pytest.mark.create_session("api_user")
def test_addon_signature_parameter(base_url, selenium, session_auth, addon_signature):
    payload = payloads.abuse_report_body("installtrigger", "about_preferences", "broken", f"{addon_signature}",
                                         "uninstall", "addon")
    create_abuse_report = requests.post(
        url=f"{base_url}{_post_abuse_report}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Session {session_auth}"
        },
        data=json.dumps(payload)
    )
    if addon_signature == "random_text":
        assert (
                create_abuse_report.status_code == 400
        ), f"Actual response: {create_abuse_report.status_code}, {create_abuse_report.text}";
        assert (
                create_abuse_report.json() == {'addon_signature': ['"random_text" is not a valid choice.']}
        ), f"Actual response: {create_abuse_report.json()}"
    else:
        assert (
                create_abuse_report.status_code == 201
        ), f"Actual response: {create_abuse_report.status_code}, {create_abuse_report.text}";
        assert (
                create_abuse_report.json()["addon_signature"] == addon_signature
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
@pytest.mark.create_session("api_user")
def test_report_entry_point_parameter(base_url, selenium, session_auth, report_entry_point):
    payload = payloads.abuse_report_body("drag_and_drop", "app_profile", "policy", "preliminary",
                                         f"{report_entry_point}", "addon")
    create_abuse_report = requests.post(
        url=f"{base_url}{_post_abuse_report}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Session {session_auth}"
        },
        data=json.dumps(payload)
    )
    if report_entry_point == "random_text":
        assert (
                create_abuse_report.status_code == 400
        ), f"Actual response: {create_abuse_report.status_code}, {create_abuse_report.text}";
        assert (
                create_abuse_report.json() == {'report_entry_point': ['"random_text" is not a valid choice.']}
        ), f"Actual response: {create_abuse_report.json()}"
    else:
        assert (
                create_abuse_report.status_code == 201
        ), f"Actual response: {create_abuse_report.status_code}, {create_abuse_report.text}";
        assert (
                create_abuse_report.json()["report_entry_point"] == report_entry_point
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
@pytest.mark.create_session("api_user")
def test_location_parameter(base_url, selenium, session_auth, location):
    payload = payloads.abuse_report_body("link", "amo", "settings", "signed", "menu", f"{location}")
    create_abuse_report = requests.post(
        url=f"{base_url}{_post_abuse_report}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Session {session_auth}"
        },
        data=json.dumps(payload)
    )
    if location == "random_text":
        assert (
                create_abuse_report.status_code == 400
        ), f"Actual response: {create_abuse_report.status_code}, {create_abuse_report.text}";
        assert (
                create_abuse_report.json() == {'location': ['"random_text" is not a valid choice.']}
        ), f"Actual response: {create_abuse_report.json()}"
    else:
        assert (
                create_abuse_report.status_code == 201
        ), f"Actual response: {create_abuse_report.status_code}, {create_abuse_report.text}";
        assert (
                create_abuse_report.json()["location"] == location
        ), f"Actual response: {create_abuse_report.json()}"
