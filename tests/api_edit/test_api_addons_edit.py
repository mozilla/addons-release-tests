import json
import time

import pytest
import requests

from api import payloads, api_helpers
from pages.desktop.frontend.home import Home
from scripts import reusables

# endpoints used in the addon edit tests
_upload = "/api/v5/addons/upload/"
_addon_create = "/api/v5/addons/addon/"

# These tests are covering various valid and invalid scenarios for editing
# listed addon details such as: name, slug, summary, description, categories,
# homepage, support site, support email, visibility, contribution urls, tags.

# API endpoints covered are:
# submit new addons: https://addons-server.readthedocs.io/en/latest/topics/api/addons.html#create
# edit addon details: https://addons-server.readthedocs.io/en/latest/topics/api/addons.html#edit
# add addon icons: https://addons-server.readthedocs.io/en/latest/topics/api/addons.html#addon-icon
# add addon screenshots: https://addons-server.readthedocs.io/en/latest/topics/api/addons.html#preview-create
# edit addon screenshots: https://addons-server.readthedocs.io/en/latest/topics/api/addons.html#preview-edit
# delete addon screenshots: https://addons-server.readthedocs.io/en/latest/topics/api/addons.html#preview-delete


@pytest.mark.serial
@pytest.mark.login("api_user")
def test_upload_listed_extension_tc_id_c4369(base_url, selenium, session_auth):
    session_cookie = selenium.get_cookie("sessionid")
    with open("sample-addons/listed-addon.zip", "rb") as file:
        upload = requests.post(
            url=f"{base_url}{_upload}",
            headers={"Authorization": f'Session {session_cookie["value"]}'},
            files={"upload": file},
            data={"channel": "listed"},
        )
    resp = upload.json()
    print(json.dumps(resp, indent=2))
    upload.raise_for_status()
    assert "listed" in resp["channel"]
    # get the addon uuid generated after upload
    uuid = resp["uuid"]
    payload = payloads.listed_addon_details(uuid)
    # sleep to allow the first request to be processed
    time.sleep(10)
    create_addon = requests.post(
        url=f"{base_url}{_addon_create}",
        headers={
            "Authorization": f'Session {session_cookie["value"]}',
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
    )
    print(create_addon)
    create_addon.raise_for_status()
    response = create_addon.json()
    print(json.dumps(response, indent=2))
    # verify that the data we sent has been registered correctly in the response we get
    api_helpers.verify_addon_response_details(payload, response, "create")


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_listed_addon_details(base_url, session_auth):
    payload = payloads.edit_addon_details
    edit_addon = requests.patch(
        url=f"{base_url}{_addon_create}my_sluggish_slug/",
        headers={
            "Authorization": f"Session {session_auth}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
    )
    edit_addon.raise_for_status()
    response = edit_addon.json()
    print(json.dumps(response, indent=2))
    # verify that the data we sent has been registered correctly in the response we get
    api_helpers.verify_addon_response_details(payload, response, "edit")


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_extension_add_invalid_categories(base_url, session_auth):
    """Try to upload an addon that has invalid android categories set in the JSON payload"""
    with open("sample-addons/listed-addon.zip", "rb") as file:
        upload = requests.post(
            url=f"{base_url}{_upload}",
            headers={"Authorization": f"Session {session_auth}"},
            files={"upload": file},
            data={"channel": "listed"},
        )
    upload.raise_for_status()
    # sleep to allow the first request to be processed
    time.sleep(3)
    print(upload.json())
    # get the addon uuid generated after upload
    uuid = upload.json()["uuid"]
    invalid_android_catg = ["", 123, None]
    for item in invalid_android_catg:
        payload = {
            **payloads.listed_addon_details(uuid),
            "categories": [item],
            "slug": "invalid-cat",
        }
        create_addon = requests.post(
            url=f"{base_url}{_addon_create}",
            headers={
                "Authorization": f"Session {session_auth}",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload),
        )
        print(
            f'For android category "{item}": Response status is {create_addon.status_code}; {create_addon.text}\n'
        )
        assert (
            create_addon.status_code == 400
        ), f"Actual status code was {create_addon.status_code}"
        assert (
            "Invalid category name" in create_addon.text
        ), f"Actual response message was {create_addon.text}"

@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_extension_one_category_and_other_category(base_url, session_auth):
    """Try to upload an addon that has invalid android categories set in the JSON payload"""
    with open("sample-addons/listed-addon.zip", "rb") as file:
        upload = requests.post(
            url=f"{base_url}{_upload}",
            headers={"Authorization": f"Session {session_auth}"},
            files={"upload": file},
            data={"channel": "listed"},
        )
    upload.raise_for_status()
    # sleep to allow the first request to be processed
    time.sleep(3)
    print(upload.json())
    # get the addon uuid generated after upload
    uuid = upload.json()["uuid"]
    invalid_android_catg = ["Appearance"]
    for item in invalid_android_catg:
        payload = {
            **payloads.listed_addon_details(uuid),
            "categories": ["Other", item],
            "slug": "invalid-cat",
        }
        create_addon = requests.post(
            url=f"{base_url}{_addon_create}",
            headers={
                "Authorization": f"Session {session_auth}",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload),
        )
        print(
            f'For android category "{item}": Response status is {create_addon.status_code}; {create_addon.text}\n'
        )
        assert (
            create_addon.status_code == 400
        ), f"Actual status code was {create_addon.status_code}"
        assert (
            "Invalid category name" in create_addon.text
        ), f"Actual response message was {create_addon.text}"

@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_extension_add_invalid_firefox_categories(base_url, session_auth):
    """Try to upload an addon that has invalid firefox categories set in the JSON payload"""
    with open("sample-addons/listed-addon.zip", "rb") as file:
        upload = requests.post(
            url=f"{base_url}{_upload}",
            headers={"Authorization": f"Session {session_auth}"},
            files={"upload": file},
            data={"channel": "listed"},
        )
    upload.raise_for_status()
    # sleep to allow the first request to be processed
    time.sleep(3)
    print(upload.json())
    # get the addon uuid generated after upload
    uuid = upload.json()["uuid"]
    invalid_firefox_catg = ["fashion", "security-privacy", "", 12.3]
    for item in invalid_firefox_catg:
        payload = {
            **payloads.listed_addon_details(uuid),
            "categories": {"android": ["performance"], "firefox": [item]},
            "slug": "invalid-firefox-cat",
        }
        create_addon = requests.post(
            url=f"{base_url}{_addon_create}",
            headers={
                "Authorization": f"Session {session_auth}",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload),
        )
        print(
            f'For firefox category "{item}": Response status is {create_addon.status_code}; {create_addon.text}\n'
        )
        assert (
            create_addon.status_code == 400
        ), f"Actual status code was {create_addon.status_code}"
        assert (
            "Invalid category name." in create_addon.text
        ), f"Actual response message was {create_addon.text}"


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_extension_other_category_is_standalone(base_url, session_auth):
    """Extensions with a category set to 'other' cannot have another category set"""
    with open("sample-addons/listed-addon.zip", "rb") as file:
        upload = requests.post(
            url=f"{base_url}{_upload}",
            headers={"Authorization": f"Session {session_auth}"},
            files={"upload": file},
            data={"channel": "listed"},
        )
    upload.raise_for_status()
    # sleep to allow the first request to be processed
    time.sleep(3)
    print(upload.json())
    # get the addon uuid generated after upload
    uuid = upload.json()["uuid"]
    payload = {
        **payloads.listed_addon_details(uuid),
        "categories": {
            "android": ["other", "performance"],
            "firefox": ["other", "bookmarks"],
        },
        "slug": "other-category",
    }
    create_addon = requests.post(
        url=f"{base_url}{_addon_create}",
        headers={
            "Authorization": f"Session {session_auth}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
    )
    assert (
        create_addon.status_code == 400
    ), f"Actual status code was {create_addon.status_code}"
    assert (
        'The \\"other\\" category cannot be combined with another category'
        in create_addon.text
    ), f"Actual response message was {create_addon.text}"


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_extension_invalid_slug(base_url, session_auth):
    """Addon slugs can be composed only from letters and numbers"""
    with open("sample-addons/listed-addon.zip", "rb") as file:
        upload = requests.post(
            url=f"{base_url}{_upload}",
            headers={"Authorization": f"Session {session_auth}"},
            files={"upload": file},
            data={"channel": "listed"},
        )
    upload.raise_for_status()
    # sleep to allow the first request to be processed
    time.sleep(3)
    print(upload.json())
    # get the addon uuid generated after upload
    uuid = upload.json()["uuid"]
    invalid_slugs = [102030, "---", "?name", "@#_" ")(", None]
    for item in invalid_slugs:
        # crete a new dictionary from the original payload, with invalid slug values
        payload = {**payloads.listed_addon_details(uuid), "slug": item}
        create_addon = requests.post(
            url=f"{base_url}{_addon_create}",
            headers={
                "Authorization": f"Session {session_auth}",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload),
        )
        print(
            f'For slug "{item}": Response status is {create_addon.status_code}; {create_addon.text}\n'
        )
        assert (
            create_addon.status_code == 400
        ), f"Actual status code was {create_addon.status_code}"
        if item == invalid_slugs[0]:  # slugs cannot contain only digits either
            assert (
                "This slug cannot be used. Please choose another." in create_addon.text
            ), f"Actual response message was {create_addon.text}"
        else:
            assert (
                "Enter a valid “slug” consisting of letters, numbers, underscores or hyphens."
                in create_addon.text
            ), f"Actual response message was {create_addon.text}"


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_extension_duplicate_slug(base_url, session_auth, variables):
    """Use a slug that already belongs to another addon"""
    addon = payloads.edit_addon_details["slug"]
    payload = {
        **payloads.edit_addon_details,
        "slug": variables["approved_addon_with_sources"],
    }
    edit_addon = requests.patch(
        url=f"{base_url}{_addon_create}{addon}/",
        headers={
            "Authorization": f"Session {session_auth}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
    )
    assert (
        edit_addon.status_code == 400
    ), f"Actual status code was {edit_addon.status_code}"
    assert (
        "addon with this slug already exists." in edit_addon.text
    ), f"Actual response message was {edit_addon.text}"


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_extension_invalid_name(base_url, session_auth):
    """Addon names are required to have at least one letter or number character to be valid"""
    addon = payloads.edit_addon_details["slug"]
    invalid_names = ["", ".", "****", None]
    for item in invalid_names:
        # crete a new dictionary from the original payload, with invalid name values
        payload = {**payloads.edit_addon_details, "name": {"en-US": item}}
        edit_addon = requests.patch(
            url=f"{base_url}{_addon_create}{addon}/",
            headers={
                "Authorization": f"Session {session_auth}",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload),
        )
        print(
            f'For name "{item}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 400
        ), f"Actual status code was {edit_addon.status_code}"
        # check response messages based on the name value sent
        if item == "":
            assert (
                "This field may not be blank" in edit_addon.text
            ), f"Actual response message was {edit_addon.text}"
        elif item is None:
            assert (
                'A value in the default locale of \\"en-US\\" is required.'
                in edit_addon.text
            ), f"Actual response message was {edit_addon.text}"
        else:
            assert (
                "Ensure this field contains at least one letter or number character"
                in edit_addon.text
            ), f"Actual response message was {edit_addon.text}"


@pytest.mark.parametrize(
    "trademark_name",
    [
        "A Name with Firefox",
        "A Name with Mozilla",
        "A Name with Mozilla Firefox",
        "Name has FireFox",
        "Name has MOZILLA",
    ],
)
@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_extension_with_trademark_in_name(base_url, session_auth, trademark_name):
    """Verifies that addon names can't be edited to include a Mozilla or Firefox trademark"""
    addon = payloads.edit_addon_details["slug"]
    # crete a new dictionary from the original payload, with variable name values
    name = {**payloads.edit_addon_details, "name": {"en-US": trademark_name}}
    edit_addon = requests.patch(
        url=f"{base_url}{_addon_create}{addon}/",
        headers={
            "Authorization": f"Session {session_auth}",
            "Content-Type": "application/json",
        },
        data=json.dumps(name),
    )
    print(
        f'For name "{trademark_name}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
    )
    assert (
        edit_addon.status_code == 400
    ), f"Actual status code was {edit_addon.status_code}"
    # check that the trademark check error message is returned
    assert (
        "Add-on names cannot contain the Mozilla or Firefox trademarks."
        in edit_addon.text
    ), f"Actual response message was {edit_addon.text}"


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_extension_invalid_summary(base_url, session_auth):
    """Addon summaries need to be in string format and below 250 characters"""
    addon = payloads.edit_addon_details["slug"]
    over_250_summary = reusables.get_random_string(251)
    summaries = ["", over_250_summary, None]
    # crete a new dictionary from the original payload, with invalid summary values
    for item in summaries:
        payload = {**payloads.edit_addon_details, "summary": {"en-US": item}}
        edit_addon = requests.patch(
            url=f"{base_url}{_addon_create}{addon}/",
            headers={
                "Authorization": f"Session {session_auth}",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload),
        )
        print(
            f'For summary "{item}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 400
        ), f"Actual status code was {edit_addon.status_code}"
        # check response messages based on the summary value sent
        if item == "":
            assert (
                "This field may not be blank." in edit_addon.text
            ), f"Actual response message was {edit_addon.text}"
        elif item == over_250_summary:
            assert (
                "Ensure this field has no more than 250 characters." in edit_addon.text
            ), f"Actual response message was {edit_addon.text}"
        else:  # if None
            assert (
                'A value in the default locale of \\"en-US\\" is required.'
                in edit_addon.text
            ), f"Actual response message was {edit_addon.text}"


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_extension_invalid_homepage(base_url, session_auth):
    """Try to add some invalid and unaccepted homepage urls for an addon"""
    addon = payloads.edit_addon_details["slug"]
    invalid_homepage = [
        "",
        ".",
        "abc123",
        "example.com",
        "http://not-valid",
        "www.some-url.org",
        base_url,
    ]
    for item in invalid_homepage:
        # crete a new dictionary from the original payload, with variable homepage values
        homepage = {**payloads.edit_addon_details, "homepage": {"en-US": item}}
        edit_addon = requests.patch(
            url=f"{base_url}{_addon_create}{addon}/",
            headers={
                "Authorization": f"Session {session_auth}",
                "Content-Type": "application/json",
            },
            data=json.dumps(homepage),
        )
        print(
            f'For homepage "{item}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 400
        ), f"Actual status code was {edit_addon.status_code}"
        # check response messages based on the homepage value sent
        if item == "":
            assert (
                "This field may not be blank" in edit_addon.text
            ), f"Actual response message was {edit_addon.text}"
        # homepage URLs can't belong to the AMO domains
        elif item == base_url:
            assert (
                f"This field can only be used to link to external websites. URLs on {base_url} are not allowed."
                in edit_addon.text
            ), f"Actual response message was {edit_addon.text}"
        else:
            assert (
                "Enter a valid URL." in edit_addon.text
            ), f"Actual response message was {edit_addon.text}"


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_extension_invalid_support_email(base_url, session_auth):
    """Try to add some invalid and unaccepted emails for an addon"""
    addon = payloads.edit_addon_details["slug"]
    invalid_email = ["", ".", "abc123", "mail.com", "abc@defg", 123, None]
    for item in invalid_email:
        # crete a new dictionary from the original payload, with variable email values
        email = {**payloads.edit_addon_details, "support_email": {"en-US": item}}
        edit_addon = requests.patch(
            url=f"{base_url}{_addon_create}{addon}/",
            headers={
                "Authorization": f"Session {session_auth}",
                "Content-Type": "application/json",
            },
            data=json.dumps(email),
        )
        print(
            f'For email "{item}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 400
        ), f"Actual status code was {edit_addon.status_code}"
        # check response messages based on the email value sent
        if item == "":
            assert (
                "This field may not be blank" in edit_addon.text
            ), f"Actual response message was {edit_addon.text}"
        elif item is None:
            assert (
                'A value in the default locale of \\"en-US\\" is required if other translations are set.'
                in edit_addon.text
            ), f"Actual response message was {edit_addon.text}"
        else:
            assert (
                "Enter a valid email address." in edit_addon.text
            ), f"Actual response message was {edit_addon.text}"


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_extension_invalid_experimental_and_payment(base_url, session_auth):
    """Try to set the 'experimental' and 'requires_payment' fields to other values than boolean"""
    addon = payloads.edit_addon_details["slug"]
    # 'is_experimental' and 'requires_payment' can only be True or False
    invalid_values = ["", "abc123", None, 123]
    for item in invalid_values:
        # crete a new dictionary from the original payload, with variable values
        payload = {
            **payloads.edit_addon_details,
            "is_experimental": item,
            "requires_payment": item,
        }
        edit_addon = requests.patch(
            url=f"{base_url}{_addon_create}{addon}/",
            headers={
                "Authorization": f"Session {session_auth}",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload),
        )
        print(
            f'For email "{item}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 400
        ), f"Actual status code was {edit_addon.status_code}"
        # check response messages based on the values sent
        if item is None:
            assert (
                "This field may not be null." in edit_addon.text
            ), f"Actual response message was {edit_addon.text}"
        else:
            assert (
                "Must be a valid boolean." in edit_addon.text
            ), f"Actual response message was {edit_addon.text}"


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_extension_valid_contribute_domains(base_url, session_auth):
    """Add a valid contributions url to an addon; requests should be successful"""
    addon = payloads.edit_addon_details["slug"]
    valid_domains = [
        "https://www.buymeacoffee.com",
        "https://donate.mozilla.org",
        "https://flattr.com",
        "https://github.com/sponsors/",
        "https://ko-fi.com",
        "https://liberapay.com",
        "https://www.micropayment.de",
        "https://opencollective.com",
        "https://www.patreon.com",
        "https://www.paypal.com",
        "https://paypal.me",
    ]
    for item in valid_domains:
        # crete a new dictionary from the original payload, with variable domain values
        payload = {**payloads.edit_addon_details, "contributions_url": item}
        edit_addon = requests.patch(
            url=f"{base_url}{_addon_create}{addon}/",
            headers={
                "Authorization": f"Session {session_auth}",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload),
        )
        print(
            f'For domain "{item}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 200
        ), f"Actual status code was {edit_addon.status_code}"


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_extension_invalid_contribute_domains(base_url, session_auth, variables):
    """Set an invalid or an unaccepted value as the addon's contribution url;
    accepted domains are predefined and must all start with 'https'"""
    addon = payloads.edit_addon_details["slug"]
    invalid_domains = [
        "",
        123,
        "abc123",
        "https://invalid.com",
        "https://www.notbuymeacoffee.com",
        "http://donate.mozilla.org",
        "https://patreon.com",
        "https://www.paypal.me",
    ]
    for item in invalid_domains:
        # crete a new dictionary from the original payload, with variable domain values
        payload = {**payloads.edit_addon_details, "contributions_url": item}
        edit_addon = requests.patch(
            url=f"{base_url}{_addon_create}{addon}/",
            headers={
                "Authorization": f"Session {session_auth}",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload),
        )
        print(
            f'For domain "{item}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 400
        ), f"Actual status code was {edit_addon.status_code}"
        # check response messages based on the domain value sent
        if item == "":
            assert (
                "This field may not be blank" in edit_addon.text
            ), f"Actual response message was {edit_addon.text}"
        # domain starts with 'https' but is not in the accepted domains list
        elif type(item) is str and item.startswith("https://"):
            assert (
                variables["contributions_bad_request_message"] in edit_addon.text
            ), f"Actual response message was {edit_addon.text}"
        # domain is in the accepted list but starts with 'http'
        elif item == "http://donate.mozilla.org":
            assert (
                "URLs must start with https://." in edit_addon.text
            ), f"Actual response message was {edit_addon.text}"
        else:
            # if the value doesn't start with 'https' and is not in the accepted list
            assert (
                variables["contributions_bad_request_message"]
                and "URLs must start with https://." in edit_addon.text
            ), f"Actual response message was {edit_addon.text}"


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_extension_invalid_addon_tags(base_url, session_auth):
    """Try to set some invalid or unaccepted tags to an addon; valid tags are predefined"""
    addon = payloads.edit_addon_details["slug"]
    # set some invalid or combinations of invalid tags; for example,
    # a combination of a valid and an invalid tag should not be accepted
    invalid_tags = [["", "abc123"], None, [123, "search"], True]
    for item in invalid_tags:
        # crete a new dictionary from the original payload, with variable values
        payload = {**payloads.edit_addon_details, "tags": item}
        edit_addon = requests.patch(
            url=f"{base_url}{_addon_create}{addon}/",
            headers={
                "Authorization": f"Session {session_auth}",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload),
        )
        print(
            f'For tags "{item}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 400
        ), f"Actual status code was {edit_addon.status_code}"
        # check response messages based on the values sent
        if item is None:
            assert (
                "This field may not be null." in edit_addon.text
            ), f"Actual response message was {edit_addon.text}"
        elif type(item) is list:  # items stored in list but are not valid tags
            assert (
                "is not a valid choice" in edit_addon.text
            ), f"Actual response message was {edit_addon.text}"
        else:  # if values are not stored in a list
            assert (
                "Expected a list of items" in edit_addon.text
            ), f"Actual response message was {edit_addon.text}"


@pytest.mark.parametrize(
    "icon",
    [
        "img/profile_picture.png",
        "img/addon_icon.jpg",
    ],
    ids=[
        "PNG icon",
        "JPG icon",
    ],
)
@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_extension_add_valid_icon(base_url, session_auth, icon):
    """Upload a custom icon for an addon; JPG and PNG are the only accepted formats"""
    addon = payloads.edit_addon_details["slug"]
    with open(icon, "rb") as img:
        edit_addon = requests.patch(
            url=f"{base_url}{_addon_create}{addon}/",
            headers={"Authorization": f"Session {session_auth}"},
            files={"icon": img},
        )
        print(
            f'For icon "{icon}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 200
        ), f"Actual status code was {edit_addon.status_code}"
        # get the icons returned by the API and add them to a list (icons are saved in three sizes)
        r_icons = edit_addon.json()["icons"]
        user_icons = [value for value in r_icons.values()]
        # if the icon has been upload successfully, we should se '/user-media/' in the icon location
        # and not '/static-server/' which is the location for the default icon served by AMO
        for icon in user_icons:
            assert f"{base_url}/user-media/addon_icons/" in icon


@pytest.mark.parametrize(
    "count, icon",
    enumerate(
        [
            "img/bmp_icon.bmp",
            "img/static_gif.gif",
            "img/animated_png.png",
            "img/invalid_image.png",
            "img/not_square.png",
        ]
    ),
    ids=[
        "BMP icon",
        "GIF static icon",
        "PNG animated icon",
        "Non image file with a .png extension",
        "Icon not square",
    ],
)
@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_extension_add_invalid_icons(
    base_url, session_auth, count, icon, variables
):
    """Verify that requests fail if icons do not meet these acceptance criteria:
    PNG or JPG, square images, non-animated images, valid image file"""
    addon = payloads.edit_addon_details["slug"]
    with open(icon, "rb") as img:
        edit_addon = requests.patch(
            url=f"{base_url}{_addon_create}{addon}/",
            headers={"Authorization": f"Session {session_auth}"},
            files={"icon": img},
        )
        print(
            f'For icon "{icon}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 400
        ), f"Actual status code was {edit_addon.status_code}"
        # check that the validation messages expected for each image type are matching the API response
        assert variables["image_validation_messages"][count] in edit_addon.text


@pytest.mark.parametrize(
    "count, preview",
    enumerate(
        [
            "img/screenshot_3.png",
            "img/screenshot_1.jpg",
        ]
    ),
    ids=[
        "PNG image",
        "JPG image",
    ],
)
@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_extension_add_valid_screenshots(base_url, session_auth, count, preview):
    """Set valid preview images for an addon; only JPG and JPG formats are accepted"""
    addon = payloads.edit_addon_details["slug"]
    with open(preview, "rb") as img:
        edit_addon = requests.post(
            url=f"{base_url}{_addon_create}{addon}/previews/",
            headers={"Authorization": f"Session {session_auth}"},
            files={"image": img},
            data={
                "position": count
            },  # sets the order in which the previews should appear
        )
        print(
            f'For image "{preview}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 201
        ), f"Actual status code was {edit_addon.status_code}"
        # verify the image has been uploaded by checking the image location (should be '/user_media/')
        assert f"{base_url}/user-media/previews/" in edit_addon.json()["image_url"]
        assert edit_addon.json()["position"] == count


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_extension_previews_add_caption(base_url, session_auth):
    """Adds a short text for each screenshot uploaded for an addon"""
    addon = payloads.edit_addon_details["slug"]
    # capture the preview ids to be used in the PATCH request and add them to a list
    previews_id = []
    get_addon = requests.get(
        url=f"{base_url}{_addon_create}{addon}/",
        headers={"Authorization": f"Session {session_auth}"},
    )
    r = get_addon.json()
    for image in r["previews"]:
        previews_id.append(image.get("id"))
    payload = payloads.preview_captions
    # add a caption for all the available previews
    for preview in previews_id:
        edit_addon = requests.patch(
            url=f"{base_url}{_addon_create}{addon}/previews/{preview}/",
            headers={
                "Authorization": f"Session {session_auth}",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload),
        )
        response = edit_addon.json()
        assert (
            edit_addon.json()["caption"] == payload["caption"]
        ), f"Actual response was {response}"


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_extension_no_image_attached(base_url, session_auth):
    """Send a screenshot upload request without adding an image"""
    addon = payloads.edit_addon_details["slug"]
    edit_addon = requests.post(
        url=f"{base_url}{_addon_create}{addon}/previews/",
        headers={"Authorization": f"Session {session_auth}"},
    )
    assert (
        edit_addon.status_code == 400
    ), f"Actual status code was {edit_addon.status_code}"
    assert (
        "No file was submitted." in edit_addon.text
    ), f"Actual response message was {edit_addon.text}"


@pytest.mark.parametrize(
    "count, preview",
    enumerate(
        [
            "img/bmp_icon.bmp",
            "img/static_gif.gif",
            "img/animated_png.png",
            "img/invalid_image.png",
        ]
    ),
    ids=[
        "BMP screenshot",
        "GIF static screenshot",
        "PNG animated screenshot",
        "Non image file with a .png extension",
    ],
)
@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_extension_add_invalid_image(
    base_url, session_auth, count, preview, variables
):
    """Verify that requests fail if images do not meet these acceptance criteria:
    PNG or JPG, non-animated images, valid image file"""
    addon = payloads.edit_addon_details["slug"]
    with open(preview, "rb") as img:
        edit_addon = requests.post(
            url=f"{base_url}{_addon_create}{addon}/previews/",
            headers={"Authorization": f"Session {session_auth}"},
            files={"image": img},
        )
        print(
            f'For image "{preview}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 400
        ), f"Actual status code was {edit_addon.status_code}"
        # check that the validation messages expected for each image type are matching the API response
        assert variables["image_validation_messages"][count] in edit_addon.text


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_extension_delete_previews(base_url, session_auth):
    """Verify that addon previews can be deleted"""
    addon = payloads.edit_addon_details["slug"]
    # get the preview ids for the available images
    preview_ids = []
    get_addon = requests.get(
        url=f"{base_url}{_addon_create}{addon}/",
        headers={"Authorization": f"Session {session_auth}"},
    )
    r = get_addon.json()
    for image in r["previews"]:
        preview_ids.append(image.get("id"))
    for preview_id in preview_ids:
        delete_image = requests.delete(
            url=f"{base_url}{_addon_create}{addon}/previews/{preview_id}",
            headers={"Authorization": f"Session {session_auth}"},
        )
        assert (
            delete_image.status_code == 204
        ), f"Actual status code was {delete_image.status_code}"
    # get the add-on details again
    get_addon = requests.get(
        url=f"{base_url}{_addon_create}{addon}/",
        headers={"Authorization": f"Session {session_auth}"},
    )
    # check that there are no screenshots left for this addon
    assert len(get_addon.json()["previews"]) == 0


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_default_locale_with_translations(base_url, session_auth):
    """Change the 'default_locale' of the addon to another locale for which we
    already have translations for the mandatory fields - i.e. 'name' and 'summary'"""
    addon = payloads.edit_addon_details["slug"]
    # list all the addon translations and try to set them as the default locale
    available_translations = ["de", "fr", "ro"]
    for locale in available_translations:
        # crete a new dictionary from the original payload, with variable values
        payload = {**payloads.edit_addon_details, "default_locale": locale}
        edit_addon = requests.patch(
            url=f"{base_url}{_addon_create}{addon}/",
            headers={
                "Authorization": f"Session {session_auth}",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload),
        )
        print(
            f'For locale "{locale}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 200
        ), f"Actual status code was {edit_addon.status_code}"
        # check response messages based on the values sent
        addon_details = edit_addon.json()
        assert addon_details["default_locale"] == locale


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_default_locale_with_missing_translations(base_url, session_auth):
    """Change the 'default_locale' of the addon to another locale for which we
    don't have translations for all the required fields - i.e. 'homepage', 'email'"""
    addon = payloads.edit_addon_details["slug"]
    # list some locales for which there are n translations and try to set them as the default locale
    unavailable_translations = ["pl", "pt-BR"]
    for locale in unavailable_translations:
        # crete a new dictionary from the original payload, with variable values
        payload = {**payloads.edit_addon_details, "default_locale": locale}
        edit_addon = requests.patch(
            url=f"{base_url}{_addon_create}{addon}/",
            headers={
                "Authorization": f"Session {session_auth}",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload),
        )
        print(
            f'For locale "{locale}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 400
        ), f"Actual status code was {edit_addon.status_code}"
        # # check response messages based on the values sent
        assert (
            f'A value in the default locale of \\"{locale}\\" is required.'
            in edit_addon.text
        ), f"Actual response message was {edit_addon.text}"


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_default_locale_invalid_values(base_url, session_auth):
    """Use some invalid/unaccepted data types for setting a 'default_locale'"""
    addon = payloads.edit_addon_details["slug"]
    invalid_locales = ["foo", 123, None, ["de", "fr"], ""]
    for locale in invalid_locales:
        # crete a new dictionary from the original payload, with variable values
        payload = {**payloads.edit_addon_details, "default_locale": locale}
        edit_addon = requests.patch(
            url=f"{base_url}{_addon_create}{addon}/",
            headers={
                "Authorization": f"Session {session_auth}",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload),
        )
        print(
            f'For locale "{locale}": Response status is {edit_addon.status_code}; {edit_addon.text}\n'
        )
        assert (
            edit_addon.status_code == 400
        ), f"Actual status code was {edit_addon.status_code}"
        # check response messages based on the values sent
        if locale is None:
            assert (
                "This field may not be null." in edit_addon.text
            ), f"Actual response message was {edit_addon.text}"
        else:
            assert (
                f'"default_locale":["\\"{locale}\\" is not a valid choice."]'
                in edit_addon.text
            ), f"Actual response message was {edit_addon.text}"


@pytest.mark.serial
def test_edit_addon_with_incorrect_account(base_url, selenium):
    """Edit the add-on details while being authenticated with a different, non-owner developer account"""
    amo = Home(selenium, base_url).open().wait_for_page_to_load()
    # login with a user that has no authorship over the addon we want to edit
    amo.login("developer")
    session_cookie = selenium.get_cookie("sessionid")
    addon = payloads.edit_addon_details["slug"]
    # crete a new dictionary from the original payload, with a different name values
    payload = {**payloads.edit_addon_details, "name": {"en-US": "some_name"}}
    edit_addon = requests.patch(
        url=f"{base_url}{_addon_create}{addon}/",
        headers={
            "Authorization": f'Session {session_cookie["value"]}',
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
    )
    assert (
        edit_addon.status_code == 403
    ), f"Actual status code was {edit_addon.status_code}"
    assert (
        "You do not have permission to perform this action." in edit_addon.text
    ), f"Actual response message was {edit_addon.text}"
