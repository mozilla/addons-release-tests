"""Payload data used in the API addon submission tests"""

minimal_manifest = {
    'manifest_version': 2,
    'version': '1.0',
}


def listed_addon_minimal(uuid):
    """This holds only the strictly necessary properties required for successful submissions"""
    body = {
        'categories': {
            'android': ['photos-media', 'shopping'],
            'firefox': ['appearance', 'download-management'],
        },
        'version': {
            'license': 'all-rights-reserved',
            'upload': uuid,
            'compatibility': ['android', 'firefox'],
        },
    }
    return body


def listed_addon_details(uuid):
    body = {
        'categories': {
            'android': ['experimental', 'performance'],
            'firefox': ['bookmarks', 'privacy-security'],
        },
        'slug': 'my_sluggish_slug',
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
                'android': {'min': '68.0', 'max': '*'},
                'firefox': {'min': '58.0', 'max': '100.*'},
            },
        },
    }
    return body


edit_addon_details = {
    'categories': {
        'android': ['photos-media', 'shopping'],
        'firefox': ['appearance', 'download-management'],
    },
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
