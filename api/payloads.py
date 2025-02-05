"""Payload data used in the API addon submission tests"""
from scripts import reusables

minimal_manifest = {
    'manifest_version': 2,
    'version': '1.0',
}


def listed_addon_minimal(uuid):
    """This holds only the strictly necessary properties required for successful submissions"""
    body = {
        'categories': ['appearance', 'download-management'],
        'version': {
            'license': 'all-rights-reserved',
            'upload': uuid,
            'compatibility': ['android', 'firefox'],
        },
    }
    return body


def listed_addon_details(uuid):
    body = {
        'categories': ['bookmarks', 'privacy-security'],
        'slug': 'my_sluggish_slug_api',
        'default_locale': 'en-US',
        'name': {
            'de': 'DE Name set at creation time',
            'en-US': 'EN-US Name set at creation time',
            'fr': 'FR Name set at creation time',
        },
        'summary': {
            'de': 'Summary, in german',
            'en-US': 'Summary, in en-US',
            'fr': 'Summary, in french',
        },
        'description': {
            'de': 'Description in german',
            'en-US': 'Description in en-US',
            'fr': 'Description in french',
        },
        'developer_comments': {
            'de': 'Dev comments in german',
            'en-US': 'Dev comments in en-US',
            'fr': 'Dev comments in french',
        },
        'homepage': {
            'de': 'https://addons.not-allizom.de',
            'en-US': 'https://addons.not-allizom.org',
            'fr': 'https://addons.not-allizom.fr',
        },
        'support_email': {
            'de': 'lang-de@mail.com',
            'en-US': 'lang-en-us@mail.com',
            'fr': 'lang-fr@mail.com',
        },
        'is_experimental': True,
        'requires_payment': True,
        'contributions_url': 'https://www.patreon.com',
        'tags': [
            'anti malware',
            'anti tracker',
            'antivirus',
            'chat',
            'container',
            'content blocker',
            'coupon',
            'dailymotion',
            'dark mode',
        ],
        'version': {
            'upload': uuid,
            'license': 'all-rights-reserved',
            'release_notes': {
                'de': 'DE Version notes added in API at addon creation time',
                'en-US': 'EN-US Version notes added in API at addon creation time',
                'fr': 'FR Version notes added in API at addon creation time',
            },
            'compatibility': {
                'android': {'min': '121.0a1', 'max': '*'},
                'firefox': {'min': '58.0', 'max': '100.*'},
            },
        },
    }
    return body


edit_addon_details = {
    'categories': ['appearance', 'download-management'],
    'slug': 'new_sluggish_slug',
    'name': {
        'de': 'DE Name edited',
        'en-US': 'EN-US Name edited',
        'fr': 'FR Name edited',
        'ro': 'RO Name edited',
    },
    'summary': {
        'de': 'Summary, in german edited',
        'en-US': 'Summary, in en-US edited',
        'fr': 'Summary, in french edited',
        'ro': 'Summary in romanian edited',
    },
    'description': {
        'de': 'Description in german edited',
        'en-US': 'Description in en-US edited',
        'fr': 'Description in french edited',
        'ro': 'Description in romanian edited',
    },
    'developer_comments': {
        'de': 'Dev comments in german edited',
        'en-US': 'Dev comments in en-US edited',
        'fr': 'Dev comments in french edited',
        'ro': 'Dev comments in romanian edited',
    },
    'homepage': {
        'de': 'https://addons.edited-allizom.de',
        'en-US': 'https://addons.edited-allizom.org',
        'fr': 'https://addons.not-allizom.fr',
        'ro': 'https://addons.not-allizom.ro',
    },
    'support_email': {
        'de': 'lang-de-edited@mail.com',
        'en-US': 'lang-en-us-edited@mail.com',
        'fr': 'lang-fr@mail.com',
        'ro': 'lang-ro@mail.com',
    },
    'support_url': {
        'de': 'https://donate.mozilla.org',
        'en-US': 'https://donate.mozilla.org',
        'fr': 'https://donate.mozilla.org',
        'ro': 'https://donate.mozilla.org'
    },
    'is_experimental': False,
    'requires_payment': False,
    'contributions_url': 'https://donate.mozilla.org',
    'tags': [
        'dndbeyond',
        'download',
        'duckduckgo',
        'facebook',
        'google',
        'mp3',
        'music',
        'password manager',
        'pinterest',
    ],
}

preview_captions = {
    'caption': {
        'de': 'Image caption in german',
        'en-US': 'Image caption in english',
        'fr': 'Image caption in french',
    }
}

edit_version_details = {
    'license': 'MPL-2.0',
    'release_notes': {
        'de': 'Edited DE Version notes added in API at addon creation time',
        'en-US': 'Edited EN-US Version notes added in API at addon creation time',
        'fr': 'Edited FR Version notes added in API at addon creation time',
        'ro': 'Edited FR Version notes added in API at addon creation time',
    },
    'compatibility': {
        'android': {'min': '121.0a1', 'max': '*'},
        'firefox': {'min': '89.0', 'max': '100.*'},
    },
}


def new_version_details(uuid):
    body = {
        "upload": uuid,
        "license": "ISC",
        "release_notes": {
            "de": "New Version DE notes added in API at addon creation time",
            "en-US": "New Version EN-US notes added in API at addon creation time",
            "fr": "New Version FR notes added in API at addon creation time",
        },
        "compatibility": {
            "android": {"min": "121.0a1", "max": "*"},
            "firefox": {"min": "70.0a1", "max": "*"},
        },
    }
    return body


def lang_tool_details(uuid):
    body = {
        'slug': f'langpack-{reusables.get_random_string(10)}',
        'categories': ['general'],
        'version': {'license': 'MPL-2.0', 'upload': uuid, 'compatibility': ['firefox']},
    }
    return body


custom_license = {
    'custom_license': {
        'name': {
            'de': 'DE Custom License Name',
            'en-US': 'EN Custom License Name',
            'fr': 'FR Custom License Name',
        },
        'text': {
            'de': 'DE Custom License Text',
            'en-US': 'EN Custom License Text',
            'fr': 'FR Custom License Text',
        },
    }
}


def theme_details(uuid, theme_license):
    body = {
        "categories": ['nature'],
        "summary": {
            "en-US": "theme summary api submissions"
        },
        "version": {
            "license": theme_license,
            "upload": uuid,
            "compatibility": ["firefox"]
        }
    }
    return body


author_stats = {
    "role": "developer",
    "listed": False,
    "position": 0
}

abuse_report_full_body = {
        "addon": "{463b483d-6150-43c9-9b52-a3d08d5ecd3a}",
        "message": "test from the API,both",
        "reason": "settings",
        "install_date": "2023-10-10T15:00:14Z",
        "addon_name": "automation-abuse-report-add-on",
        "report_entry_point": "amo",
        "addon_install_method": "link",
        "addon_install_origin": "https://addons-server.readthedocs.io/en/latest/topics/api/abuse.html",
        "addon_install_source": "amo",
        "addon_install_source_url": "https://addons.allizom.org/en-US/firefox/addon/automation-abuse-report-add-on/",
        "addon_signature": "signed",
        "addon_summary": "Random summary",
        "addon_version": "1.1",
        "app": "firefox",
        "appversion": "1.1",
        "lang": "en-Us",
        "client_id": "06ecc8cef773a56ce40baa1ca1237184ea2c6a6a7f0485eda1ea7f4b5c317c65",
        "operating_system": "windows",
        "operating_system_version": "10",
        "location": "amo",
        "reporter_name": "A name",
        "reporter_email": "reporter@test.com"
}

def abuse_report_body(addon_install_method, addon_install_source, reason, addon_signature, report_entry_point, location):
    body = {
        "addon": "{463b483d-6150-43c9-9b52-a3d08d5ecd3a}",
        "message": "test from the API,both",
        "reason": reason,
        "install_date": "2023-10-10T15:00:14Z",
        "addon_name": "automation-abuse-report-add-on",
        "report_entry_point": report_entry_point,
        "addon_install_method": addon_install_method,
        "addon_install_origin": "https://addons-server.readthedocs.io/en/latest/topics/api/abuse.html",
        "addon_install_source": addon_install_source,
        "addon_install_source_url": "https://addons-dev.allizom.org/en-US/firefox/addon/desktop_android_addon/",
        "addon_signature": addon_signature,
        "addon_summary": "Listed extension for release testing",
        "addon_version": "10.151",
        "app": "firefox",
        "appversion": "118.0.1",
        "lang": "en-US",
        "client_id": "06ecc8cef773a56ce40baa1ca1237184ea2c6a6a7f0485eda1ea7f4b5c317c65",
        "operating_system": "windows",
        "operating_system_version": "10",
        "location": location,
        "reporter_name": "A name",
        "reporter_email": "reporter@test.com"
    }
    return body
