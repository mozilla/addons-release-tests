import json
import time

import pytest
import requests

from api import payloads, api_helpers

from scripts import reusables

# endpoints used in the version edit tests
_addon_create = "/api/v5/addons/addon/"
_upload = "/api/v5/addons/upload/"

# These tests are covering various valid and invalid scenarios for editing
# addon version details such as: compatibility, license, release notes, source code,
# uploading new versions, deleting the addons;

# API endpoints covered are:
# create a new version: https://addons-server.readthedocs.io/en/latest/topics/api/addons.html#version-create
# edit version details: https://addons-server.readthedocs.io/en/latest/topics/api/addons.html#version-edit
# create new version with PUT: https://addons-server.readthedocs.io/en/latest/topics/api/addons.html#put-create-or-edit
# upload source code: https://addons-server.readthedocs.io/en/latest/topics/api/addons.html#version-sources
# delete addons: https://addons-server.readthedocs.io/en/latest/topics/api/addons.html#delete


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_version_details(base_url, session_auth):
    """Edit the version specific fields, i.e. 'release_notes', 'license, 'compatibility'"""
    addon = payloads.edit_addon_details["slug"]
    request = requests.get(
        url=f"{base_url}{_addon_create}{addon}",
        headers={"Authorization": f"Session {session_auth}"},
    )
    # get the version id of the version we want to edit
    version = request.json()["current_version"]["id"]
    payload = payloads.edit_version_details
    edit_version = requests.patch(
        url=f"{base_url}{_addon_create}{addon}/versions/{version}/",
        headers={
            "Authorization": f"Session {session_auth}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
    )
    edit_version.raise_for_status()
    response = edit_version.json()
    # verify that the data we sent has been registered correctly in the response we get
    assert payload["license"] == response["license"]["slug"]
    assert payload["compatibility"] == response["compatibility"]
    assert payload["release_notes"] == response["release_notes"]


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_version_custom_license_no_text(base_url, session_auth):
    """When setting a custom license, it is mandatory for that license to contain a text"""
    addon = payloads.edit_addon_details["slug"]
    request = requests.get(
        url=f"{base_url}{_addon_create}{addon}",
        headers={"Authorization": f"Session {session_auth}"},
    )
    # get the version id of the version we want to edit
    version = request.json()["current_version"]["id"]
    payload = {
        **payloads.custom_license,
        "custom_license": {"name": {"en-US": "no-text-provided"}},
    }
    edit_version = requests.patch(
        url=f"{base_url}{_addon_create}{addon}/versions/{version}/",
        headers={
            "Authorization": f"Session {session_auth}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
    )
    assert (
        edit_version.status_code == 400
    ), f"Actual status code was {edit_version.status_code}"
    assert (
        '{"custom_license":{"text":["This field is required."]}}' in edit_version.text
    ), f"Actual response message was {edit_version.text}"


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_version_set_custom_license(base_url, session_auth):
    """Instead of using a predefined addon license provided by AMO, add a
    custom license with 'name' and 'text' defined by the addon author"""
    addon = payloads.edit_addon_details["slug"]
    request = requests.get(
        url=f"{base_url}{_addon_create}{addon}",
        headers={"Authorization": f"Session {session_auth}"},
    )
    # get the version id of the version we want to edit
    version = request.json()["current_version"]["id"]
    payload = payloads.custom_license
    edit_version = requests.patch(
        url=f"{base_url}{_addon_create}{addon}/versions/{version}/",
        headers={
            "Authorization": f"Session {session_auth}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
    )
    edit_version.raise_for_status()
    response = edit_version.json()
    assert payload["custom_license"]["name"] == response["license"]["name"]
    assert payload["custom_license"]["text"] == response["license"]["text"]


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_upload_new_listed_version(base_url, session_auth):
    """Uploads a new listed version for an existing addon"""
    with open("sample-addons/listed-addon-new-version.zip", "rb") as file:
        upload = requests.post(
            url=f"{base_url}{_upload}",
            headers={"Authorization": f"Session {session_auth}"},
            files={"upload": file},
            data={"channel": "listed"},
        )
    time.sleep(5)
    upload.raise_for_status()
    # get the addon uuid generated after upload
    uuid = upload.json()["uuid"]
    addon = payloads.edit_addon_details["slug"]
    payload = payloads.new_version_details(uuid)
    new_version = requests.post(
        url=f"{base_url}{_addon_create}{addon}/versions/",
        headers={
            "Authorization": f"Session {session_auth}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
    )
    new_version.raise_for_status()
    response = new_version.json()
    # verify that the new version was created with the data provided
    assert response["version"] == "1.1"
    assert payload["license"] == response["license"]["slug"]
    assert payload["compatibility"] == response["compatibility"]
    assert payload["release_notes"] == response["release_notes"]


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_upload_new_version_with_existing_version_number(base_url, session_auth):
    """Uploads a new version with an existing version number; the upload should fail"""
    with open("sample-addons/listed-addon-new-version.zip", "rb") as file:
        upload = requests.post(
            url=f"{base_url}{_upload}",
            headers={"Authorization": f"Session {session_auth}"},
            files={"upload": file},
            data={"channel": "listed"},
        )
    time.sleep(5)
    upload.raise_for_status()
    # get the addon uuid generated after upload
    uuid = upload.json()["uuid"]
    addon = payloads.edit_addon_details["slug"]
    payload = payloads.new_version_details(uuid)
    new_version = requests.post(
        url=f"{base_url}{_addon_create}{addon}/versions/",
        headers={
            "Authorization": f"Session {session_auth}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
    )
    assert (
        new_version.status_code == 409
    ), f"Actual response: status code = {new_version.status_code}, message = {new_version.text}"
    assert (
        "Version 1.1 already exists." in new_version.text
    ), f"Actual response message was {new_version.text}"


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_upload_new_unlisted_version_with_put_method(base_url, session_auth):
    """Takes an addon with listed version only and submits an unlisted version;
    this is creating an addon with mixed versions. Use the PUT endpoint in this
     case to check that it also works for a new version submission process"""
    addon = payloads.edit_addon_details["slug"]
    # get the addon guid required for the PUT method
    get_addon_details = requests.get(
        url=f"{base_url}{_addon_create}{addon}/",
        headers={"Authorization": f"Session {session_auth}"},
    )
    guid = get_addon_details.json()["guid"]
    # upload a new unlisted version
    with open("sample-addons/mixed-addon-versions.zip", "rb") as file:
        upload = requests.post(
            url=f"{base_url}{_upload}",
            headers={"Authorization": f"Session {session_auth}"},
            files={"upload": file},
            data={"channel": "unlisted"},
        )
    time.sleep(5)
    upload.raise_for_status()
    resp = upload.json()
    # verify that the upload was created as unlisted
    assert "unlisted" in resp["channel"]
    # get the addon uuid generated after upload
    uuid = resp["uuid"]
    new_version = requests.put(
        url=f"{base_url}{_addon_create}{guid}/",
        headers={
            "Authorization": f"Session {session_auth}",
            "Content-Type": "application/json",
        },
        data=json.dumps({"version": {"upload": uuid}}),
    )
    new_version.raise_for_status()
    response = new_version.json()
    # this property needs to exist if the unlisted submission was successful
    return response["latest_unlisted_version"]["id"]


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_upload_new_version_with_different_addon_type(base_url, session_auth):
    """Take an exiting addon of type 'extensions' and try to upload a new version
    of type 'statictheme' for it; the submission should fail"""
    with open("sample-addons/theme.xpi", "rb") as file:
        upload = requests.post(
            url=f"{base_url}{_upload}",
            headers={"Authorization": f"Session {session_auth}"},
            files={"upload": file},
            data={"channel": "listed"},
        )
    time.sleep(5)
    upload.raise_for_status()
    # get the addon uuid generated after upload
    uuid = upload.json()["uuid"]
    addon = payloads.edit_addon_details["slug"]
    payload = {"upload": uuid}
    new_version = requests.post(
        url=f"{base_url}{_addon_create}{addon}/versions/",
        headers={
            "Authorization": f"Session {session_auth}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
    )
    assert (
        new_version.status_code == 400
    ), f"Actual response: status code = {new_version.status_code}, message = {new_version.text}"
    assert (
        "The type (10) does not match the type of your add-on on AMO (1)"
        in new_version.text
    ), f"Actual response message was {new_version.text}"


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_upload_new_version_with_different_guid(base_url, session_auth):
    """Take an exiting addon and submit a new version that has a different GUID
    from what we have on AMO for this addon; the submission should fail"""
    guid = f"random-guid@{reusables.get_random_string(6)}"
    # create the addon manifest to be uploaded
    manifest = {
        **payloads.minimal_manifest,
        "version": "2.0",
        "name": "New version with different guid",
        "browser_specific_settings": {"gecko": {"id": guid}},
    }
    api_helpers.make_addon(manifest)
    with open("sample-addons/make-addon.zip", "rb") as file:
        upload = requests.post(
            url=f"{base_url}{_upload}",
            headers={"Authorization": f"Session {session_auth}"},
            files={"upload": file},
            data={"channel": "listed"},
        )
    time.sleep(5)
    upload.raise_for_status()
    # get the addon uuid generated after upload
    uuid = upload.json()["uuid"]
    addon = payloads.edit_addon_details["slug"]
    payload = {"upload": uuid}
    new_version = requests.post(
        url=f"{base_url}{_addon_create}{addon}/versions/",
        headers={
            "Authorization": f"Session {session_auth}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
    )
    assert (
        new_version.status_code == 400
    ), f"Actual response: status code = {new_version.status_code}, message = {new_version.text}"
    assert (
        f"The add-on ID in your manifest.json ({guid}) does not match the ID of your add-on on AMO"
        in new_version.text
    ), f"Actual response message was {new_version.text}"


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_upload_new_version_with_sources(base_url, session_auth):
    """Uploads a new version for an exiting addon while also attaching additional source code"""
    manifest = {
        **payloads.minimal_manifest,
        "name": "EN-US Name edited",
        "version": "3.0",
    }
    api_helpers.make_addon(manifest)
    with open("sample-addons/make-addon.zip", "rb") as file:
        upload = requests.post(
            url=f"{base_url}{_upload}",
            headers={"Authorization": f"Session {session_auth}"},
            files={"upload": file},
            data={"channel": "listed"},
        )
    time.sleep(5)
    upload.raise_for_status()
    # get the addon uuid generated after upload
    uuid = upload.json()["uuid"]
    addon = payloads.edit_addon_details["slug"]
    # submit the version and attach source code
    with open("sample-addons/listed-addon.zip", "rb") as source:
        new_version = requests.post(
            url=f"{base_url}{_addon_create}{addon}/versions/",
            headers={"Authorization": f"Session {session_auth}"},
            data={"upload": uuid},
            files={"source": source},
        )
    response = new_version.json()
    new_version.raise_for_status()
    # verify that the 'source' field doesn't return null in the API response
    assert f"{base_url}/firefox/downloads/source/" in response["source"]
    url = response["source"]
    # compare the actual source file uploaded with the one returned by the API to make sure they match
    response_source = requests.get(url, cookies={"sessionid": session_auth}, timeout=10)
    api_helpers.compare_source_files(
        "sample-addons/listed-addon.zip", response_source, "POST"
    )


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_version_change_sources(base_url, session_auth):
    """Upload different source file for an existing version and make sure that changes were applied"""
    addon = payloads.edit_addon_details["slug"]
    request = requests.get(
        url=f"{base_url}{_addon_create}{addon}",
        headers={"Authorization": f"Session {session_auth}"},
    )
    # get the version id of the version we want to edit
    version = request.json()["current_version"]["id"]
    get_old_source = requests.get(
        url=f"{base_url}{_addon_create}{addon}/versions/{version}/",
        headers={"Authorization": f"Session {session_auth}"},
    )
    # download the previous source code attached to the version
    previous_source = requests.get(
        get_old_source.json()["source"], cookies={"sessionid": session_auth}, timeout=10
    )
    with open("sample-addons/unlisted-addon.zip", "rb") as source:
        change_source = requests.patch(
            url=f"{base_url}{_addon_create}{addon}/versions/{version}/",
            headers={"Authorization": f"Session {session_auth}"},
            files={"source": source},
        )
    # download the new source code attached to the  version
    new_source = requests.get(
        change_source.json()["source"], cookies={"sessionid": session_auth}, timeout=10
    )
    # compare that the previous source and the new source do not match
    api_helpers.compare_source_files(previous_source, new_source, "PATCH")


@pytest.mark.parametrize(
    "file_type",
    [
        "tar-bz2-ext.tar.bz2",
        "tgz-ext.tgz",
        "tar-gz-ext.tar.gz",
    ],
    ids=[
        'Archive in "tar.bz2" format',
        'Archive in "tgz" format',
        'Archive in "tar.gz" format',
    ],
)
@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_version_upload_supported_source_files(base_url, session_auth, file_type):
    """Upload all the supported source file types and make sure the request is successful"""
    addon = payloads.edit_addon_details["slug"]
    request = requests.get(
        url=f"{base_url}{_addon_create}{addon}",
        headers={"Authorization": f"Session {session_auth}"},
    )
    # get the version id of the version we want to edit
    version = request.json()["current_version"]["id"]
    with open(f"sample-addons/{file_type}", "rb") as file:
        upload_source = requests.patch(
            url=f"{base_url}{_addon_create}{addon}/versions/{version}/",
            headers={"Authorization": f"Session {session_auth}"},
            files={"source": file},
        )
    assert (
        upload_source.status_code == 200
    ), f'For file_type "{file_type}", status code = {upload_source.status_code}, message = {upload_source.text}'
    # verify that the file upload was successful by comparing the uploaded file with the file returned by the API
    response = upload_source.json()
    url = response["source"]
    response_source = requests.get(url, cookies={"sessionid": session_auth}, timeout=10)
    api_helpers.compare_source_files(
        f"sample-addons/{file_type}", response_source, "post"
    )


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_sources_cannot_be_changed_for_approved_versions(
    base_url, session_auth, variables
):
    """Addons that were Approved by a reviewer can't have their source files changed"""
    addon = variables["approved_addon_with_sources"]
    request = requests.get(
        url=f"{base_url}{_addon_create}{addon}",
        headers={"Authorization": f"Session {session_auth}"},
    )
    # get the version id of the version we want to edit
    version = request.json()["current_version"]["id"]
    with open("sample-addons/source-img.zip", "rb") as file:
        upload_source = requests.patch(
            url=f"{base_url}{_addon_create}{addon}/versions/{version}/",
            headers={"Authorization": f"Session {session_auth}"},
            files={"source": file},
        )
    assert (
        upload_source.status_code == 400
    ), f"Actual response: {upload_source.status_code}, {upload_source.text}"
    assert (
        "Source cannot be changed because this version has been reviewed by Mozilla."
        in upload_source.text
    ), f"Actual response message was {upload_source.text}"


@pytest.mark.parametrize(
    "slug",
    [
        "",
        None,
        False,
        123,
        "random slug",
        {"value": "some value"},
    ],
    ids=[
        "Empty string",
        "None/No value",
        "Boolean",
        "Integer",
        "Random string",
        "Dictionary",
    ],
)
@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_version_invalid_license(base_url, session_auth, slug):
    """Extension license slugs have to match one of the predefined licenses accepted by AMO"""
    addon = payloads.edit_addon_details["slug"]
    request = requests.get(
        url=f"{base_url}{_addon_create}{addon}",
        headers={"Authorization": f"Session {session_auth}"},
    )
    # get the version id of the version we want to edit
    version = request.json()["current_version"]["id"]
    payload = {**payloads.edit_version_details, "license": slug}
    edit_version = requests.patch(
        url=f"{base_url}{_addon_create}{addon}/versions/{version}/",
        headers={
            "Authorization": f"Session {session_auth}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
    )
    print(
        f'For license slug "{slug}": Response status is '
        f"{edit_version.status_code}; {edit_version.text}\n"
    )
    assert (
        edit_version.status_code == 400
    ), f"Actual status code was {edit_version.status_code}"
    if slug is None:
        assert (
            "This field may not be null." in edit_version.text
        ), f"Actual response message was {edit_version.text}"
    else:
        assert (
            f"License with slug={slug} does not exist." in edit_version.text
        ), f"Actual response message was {edit_version.text}"


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_version_both_license_and_custom_license(base_url, session_auth):
    """An addon can have either a predefined license or a custom license but not both"""
    addon = payloads.edit_addon_details["slug"]
    request = requests.get(
        url=f"{base_url}{_addon_create}{addon}",
        headers={"Authorization": f"Session {session_auth}"},
    )
    # get the version id of the version we want to edit
    version = request.json()["current_version"]["id"]
    # add a custom license besides the 'license' we already have in the edit version payload
    payload = {
        **payloads.edit_version_details,
        "custom_license": {"name": {"en-US": "custom-name"}},
    }
    edit_version = requests.patch(
        url=f"{base_url}{_addon_create}{addon}/versions/{version}/",
        headers={
            "Authorization": f"Session {session_auth}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
    )
    assert (
        edit_version.status_code == 400
    ), f"Actual status code was {edit_version.status_code}"
    assert (
        "Both `license` and `custom_license` cannot be provided together."
        in edit_version.text
    ), f"Actual response message was {edit_version.text}"


@pytest.mark.parametrize(
    "value",
    [
        "",
        "all-rights-reserved",
        123,
        None,
        False,
    ],
    ids=[
        "Empty string",
        "Built in license",
        "Integer",
        "None/No value",
        "Boolean",
    ],
)
@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_version_invalid_custom_license_format(base_url, session_auth, value):
    """Custom licenses should be a dictionary containing the license name and text; other formats should fail"""
    addon = payloads.edit_addon_details["slug"]
    request = requests.get(
        url=f"{base_url}{_addon_create}{addon}",
        headers={"Authorization": f"Session {session_auth}"},
    )
    # get the version id of the version we want to edit
    version = request.json()["current_version"]["id"]
    payload = {**payloads.custom_license, "custom_license": value}
    edit_version = requests.patch(
        url=f"{base_url}{_addon_create}{addon}/versions/{version}/",
        headers={
            "Authorization": f"Session {session_auth}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
    )
    print(
        f'For custom_license "{value}": Response status is '
        f"{edit_version.status_code}; {edit_version.text}\n"
    )
    assert (
        edit_version.status_code == 400
    ), f"Actual status code was {edit_version.status_code}"
    if value is None:
        assert (
            "This field may not be null." in edit_version.text
        ), f"Actual response message was {edit_version.text}"
    else:
        assert (
            "Invalid data. Expected a dictionary" in edit_version.text
        ), f"Actual response message was {edit_version.text}"


@pytest.mark.parametrize(
    "value",
    [
        "",
        {"foo": "string"},
    ],
    ids=[
        "Not a dictionary",
        "Invalid locale",
    ],
)
@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_version_invalid_custom_license_name_and_text(
    base_url, session_auth, value
):
    """Custom licenses should be a dictionary containing the license name and text;
    also, the name and text need to be specified in a valid locale"""
    addon = payloads.edit_addon_details["slug"]
    request = requests.get(
        url=f"{base_url}{_addon_create}{addon}",
        headers={"Authorization": f"Session {session_auth}"},
    )
    # get the version id of the version we want to edit
    version = request.json()["current_version"]["id"]
    payload = {
        **payloads.custom_license,
        "custom_license": {"name": value, "text": value},
    }
    edit_version = requests.patch(
        url=f"{base_url}{_addon_create}{addon}/versions/{version}/",
        headers={
            "Authorization": f"Session {session_auth}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
    )
    print(
        f'For custom_license "{value}": Response status is '
        f"{edit_version.status_code}; {edit_version.text}\n"
    )
    assert (
        edit_version.status_code == 400
    ), f"Actual status code was {edit_version.status_code}"
    if type(value) is not dict:
        assert (
            "You must provide an object of {lang-code:value}." in edit_version.text
        ), f"Actual response message was {edit_version.text}"
    else:
        assert (
            'The language code \\"foo\\" is invalid.' in edit_version.text
        ), f"Actual response message was {edit_version.text}"


@pytest.mark.parametrize(
    "value",
    [
        "",
        None,
        False,
        123,
        "random string",
    ],
    ids=[
        "Empty string",
        "None/No value",
        "Boolean",
        "Integer",
        "Random string",
    ],
)
@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_version_invalid_compatibility_format(base_url, session_auth, value):
    """The compatibility field needs to be either a dictionary or a list; other formats should fail"""
    addon = payloads.edit_addon_details["slug"]
    request = requests.get(
        url=f"{base_url}{_addon_create}{addon}",
        headers={"Authorization": f"Session {session_auth}"},
    )
    # get the version id of the version we want to edit
    version = request.json()["current_version"]["id"]
    payload = {**payloads.edit_version_details, "compatibility": value}
    edit_version = requests.patch(
        url=f"{base_url}{_addon_create}{addon}/versions/{version}/",
        headers={
            "Authorization": f"Session {session_auth}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
    )
    print(
        f'For compatibility "{value}": Response status is '
        f"{edit_version.status_code}; {edit_version.text}\n"
    )
    assert (
        edit_version.status_code == 400
    ), f"Actual status code was {edit_version.status_code}"
    if value is None:
        assert (
            "This field may not be null." in edit_version.text
        ), f"Actual response message was {edit_version.text}"
    else:
        assert (
            "Invalid value" in edit_version.text
        ), f"Actual response message was {edit_version.text}"


@pytest.mark.parametrize(
    "request_value, response_value",
    [
        (
            ["android", "firefox"],
            {
                "android": {"min": "48.0", "max": "*"},
                "firefox": {"min": "42.0", "max": "*"},
            },
        ),
        (["firefox"], {"firefox": {"min": "42.0", "max": "*"}}),
        ({"firefox": {"min": "65.0"}}, {"firefox": {"min": "65.0", "max": "*"}}),
        ({"android": {"max": "95.0"}}, {"android": {"min": "48.0", "max": "95.0"}}),
    ],
    ids=[
        "Compatibility in list format, valid apps (firefox and android)",
        "Compatibility in list format, only firefox compatibility",
        "Valid app - firefox and valid appversion",
        "Valid app - android and valid appversion",
    ],
)
@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_version_valid_compatibility_values(
    base_url, session_auth, request_value, response_value
):
    """Tests the compatibility field with a set of valid values"""
    addon = payloads.edit_addon_details["slug"]
    request = requests.get(
        url=f"{base_url}{_addon_create}{addon}",
        headers={"Authorization": f"Session {session_auth}"},
    )
    # get the version id of the version we want to edit
    version = request.json()["current_version"]["id"]
    payload = {**payloads.edit_version_details, "compatibility": request_value}
    edit_version = requests.patch(
        url=f"{base_url}{_addon_create}{addon}/versions/{version}/",
        headers={
            "Authorization": f"Session {session_auth}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
    )
    print(
        f'For compatibility "{request_value}": Response status is '
        f"{edit_version.status_code}; {edit_version.text}\n"
    )
    r = edit_version.json()
    assert (
        edit_version.status_code == 200
    ), f"Actual status code was {edit_version.status_code}"
    # verify that the returned compatibility matches what we expect for the values sent
    assert response_value == r["compatibility"]


@pytest.mark.parametrize(
    "value",
    [
        [None, None],
        ["firefox", None],
        {"firefox": {"min": "*"}},
        {"firefox": {"min": "78.*"}},
        {"android": {"max": "99595.0"}},
        {"firefox": {"min": "*", "max": "65.0"}},
    ],
    ids=[
        "None/No values",
        "Valid app for firefox, None for android",
        'Invalid firefox min appversion - "*"',
        'Invalid firefox min appversion - "x.*"',
        "Unavailable max appversion",
        "Valid max version, invalid min version",
    ],
)
@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_version_invalid_compatibility_values(base_url, session_auth, value):
    """Compatibility values should be a combination of valid applications (firefox or android)
    and application versions (existing versions of Firefox for desktop/android)"""
    addon = payloads.edit_addon_details["slug"]
    request = requests.get(
        url=f"{base_url}{_addon_create}{addon}",
        headers={"Authorization": f"Session {session_auth}"},
    )
    # get the version id of the version we want to edit
    version = request.json()["current_version"]["id"]
    payload = {**payloads.edit_version_details, "compatibility": value}
    edit_version = requests.patch(
        url=f"{base_url}{_addon_create}{addon}/versions/{version}/",
        headers={
            "Authorization": f"Session {session_auth}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
    )
    print(
        f'For compatibility "{value}": Response status is '
        f"{edit_version.status_code}; {edit_version.text}\n"
    )
    assert (
        edit_version.status_code == 400
    ), f"Actual status code was {edit_version.status_code}"
    if type(value) is list:
        assert (
            "Invalid app specified" in edit_version.text
        ), f"Actual response message was {edit_version.text}"
    else:
        try:
            assert (
                "Unknown min app version specified" in edit_version.text
            ), f"Actual response message was {edit_version.text}"
        except AssertionError:
            assert (
                "Unknown max app version specified" in edit_version.text
            ), f"Actual response message was {edit_version.text}"


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_edit_version_disable_current_version(base_url, session_auth):
    """Disable then re-enable the current version of an addon as a developer"""
    addon = payloads.edit_addon_details["slug"]
    request = requests.get(
        url=f"{base_url}{_addon_create}{addon}",
        headers={"Authorization": f"Session {session_auth}"},
    )
    # get the version id of the version we want to edit
    version = request.json()["current_version"]["id"]
    payload = {"is_disabled": True}
    edit_version = requests.patch(
        url=f"{base_url}{_addon_create}{addon}/versions/{version}/",
        headers={
            "Authorization": f"Session {session_auth}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
    )
    assert (
        edit_version.status_code == 200
    ), f"Actual response was: {edit_version.status_code}; {edit_version.text}"
    # verify that the version has been disabled successfully
    version_status = requests.get(
        url=f"{base_url}{_addon_create}{addon}/versions/{version}/",
        headers={
            "Authorization": f"Session {session_auth}",
            "Content-Type": "application/json",
        },
    )
    assert (
        version_status.json()["is_disabled"] is True
    ), f"Actual response was: {version_status.json()}"
    # re-enable the version
    payload = {"is_disabled": False}
    edit_version = requests.patch(
        url=f"{base_url}{_addon_create}{addon}/versions/{version}/",
        headers={
            "Authorization": f"Session {session_auth}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
    )
    assert (
        edit_version.status_code == 200
    ), f"Actual response was: {edit_version.status_code}; {edit_version.text}"
    # verify that the version has been re-enabled successfully
    version_status = requests.get(
        url=f"{base_url}{_addon_create}{addon}/versions/{version}/",
        headers={
            "Authorization": f"Session {session_auth}",
            "Content-Type": "application/json",
        },
    )
    assert (
        version_status.json()["is_disabled"] is False
    ), f"Actual response was: {version_status.json()}"


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_delete_extension_non_existent_addon(base_url, session_auth):
    """Try to obtain a delete token for a non-existent addon"""
    addon = "rand-om123"
    get_delete_confirm = requests.get(
        url=f"{base_url}{_addon_create}{addon}/delete_confirm/",
        headers={"Authorization": f"Session {session_auth}"},
    )
    assert (
        get_delete_confirm.status_code == 404
    ), f"Actual response: {get_delete_confirm.status_code}, {get_delete_confirm.text}"


@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_delete_extension_from_another_author(base_url, session_auth, variables):
    """Try to delete someone else's addon; the request should fail"""
    addon = variables["detail_extension_slug"]
    get_delete_confirm = requests.get(
        url=f"{base_url}{_addon_create}{addon}/delete_confirm/",
        headers={"Authorization": f"Session {session_auth}"},
    )
    assert (
        get_delete_confirm.status_code == 403
    ), f"Actual response: {get_delete_confirm.status_code}, {get_delete_confirm.text}"
    assert (
        "You do not have permission to perform this action." in get_delete_confirm.text,
        f"Actual response message was {get_delete_confirm.text}",
    )


@pytest.mark.parametrize(
    "token",
    [
        "random-string",
        "",
        123,
        None,
    ],
    ids=[
        "Random string",
        "Empty string",
        "Integer",
        "None/No value",
    ],
)
@pytest.mark.serial
@pytest.mark.create_session("api_user")
def test_delete_extension_with_invalid_tokens(base_url, session_auth, token):
    """Use invalid formats or data types for the token required to delete an addon"""
    addon = payloads.edit_addon_details["slug"]
    delete_addon = requests.delete(
        url=f"{base_url}{_addon_create}{addon}/",
        headers={"Authorization": f"Session {session_auth}"},
        params={"delete_confirm": token},
    )
    assert (
        delete_addon.status_code == 400
    ), f'For token "{token}", status code = {delete_addon.status_code}, message = {delete_addon.text}'
    if token is None or token == "":
        assert (
            "token must be supplied for add-on delete" in delete_addon.text
        ), f"Actual response message was {delete_addon.text}"
    else:
        assert (
            "token is invalid" in delete_addon.text
        ), f'For token "{token}", status code = {delete_addon.status_code}, message = {delete_addon.text}'


@pytest.mark.serial
@pytest.mark.create_session("api_user")
@pytest.mark.clear_session
def test_delete_extension_valid_token(selenium, base_url, session_auth, variables):
    addon = payloads.edit_addon_details["slug"]
    get_delete_confirm = requests.get(
        url=f"{base_url}{_addon_create}{addon}/delete_confirm/",
        headers={"Authorization": f"Session {session_auth}"},
    )
    get_delete_confirm.raise_for_status()
    r = get_delete_confirm.json()
    token = r["delete_confirm"]
    delete_addon = requests.delete(
        url=f"{base_url}{_addon_create}{addon}/",
        headers={"Authorization": f"Session {session_auth}"},
        params={"delete_confirm": token},
    )
    assert (
        delete_addon.status_code == 204
    ), f"Actual status code was {delete_addon.status_code}"
    get_addon = requests.get(
        url=f"{base_url}{_addon_create}{addon}/",
        headers={"Authorization": f"Session {session_auth}"},
    )
    assert (
        get_addon.status_code == 404
    ), f"Actual status code was {get_addon.status_code}"
