"""File holding some reusable methods used in the API addon submission tests"""


def verify_addon_response_details(payload, response, request):
    """Method checking that the values set in the request payload are found
    in the response returned by the API. It can be used both for verifying
    new uploads and addon edits, based on the <request> argument.
    Note that payload keys and the response keys structure is different in some places."""
    assert payload['categories'] == response['categories']
    assert payload['name'] == response['name']
    assert payload['slug'] == response['slug']
    assert payload['description'] == response['description']
    assert payload['summary'] == response['summary']
    assert payload['developer_comments'] == response['developer_comments']
    assert payload['homepage'] == response['homepage']['url']
    assert payload['support_email'] == response['support_email']
    assert payload['is_experimental'] == response['is_experimental']
    assert payload['requires_payment'] == response['requires_payment']
    assert payload['tags'] == response['tags']
    if request != 'edit':
        assert (
            payload['version']['license']
            == response['current_version']['license']['slug']
        )
        assert (
            payload['version']['compatibility']
            == response['current_version']['compatibility']
        )
        assert (
            payload['version']['release_notes']
            == response['current_version']['release_notes']
        )
