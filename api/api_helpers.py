"""File holding some reusable methods used in the API addon submission tests"""


def verify_addon_response_details(payload, response, request):
    """Method checking that the values set in the request payload are found
    in the response returned by the API. It can be used both for verifying
    new uploads and addon edits, based on the <request> argument."""
    # save the request values (stored in a dictionary) in a list
    addon_details = [value for value in payload.values()]
    # capture the necessary response values from the JSON response and add them to a list
    response_values = [
        response['categories'],
        response['slug'],
        response['name'],
        response['summary'],
        response['description'],
        response['developer_comments'],
        response['homepage']['url'],
        response['support_email'],
        response['is_experimental'],
        response['requires_payment'],
        response['contributions_url']['url'].split('?')[0],
        response['tags'],
    ]
    # for new uploads, we need to check the version values as well
    if request == 'create':
        # remove the 'upload' value from the request details because it is not present in the JSON response
        addon_details[-1].pop('upload')
        # store the version request details, which are stored in a nested dict inside
        # the 'addon details' dict, in a separate list
        version_details = addon_details[-1].values()
        # remove the dictionary from the 'addon details' initial list
        # and replace it with the individual values stored in the 'version_details' list
        addon_details.pop()
        addon_details.extend([detail for detail in version_details])
        # extend the response values to include the 'current_version' details
        response_values.extend(
            [
                response['current_version']['license']['slug'],
                response['current_version']['release_notes'],
                response['current_version']['compatibility'],
            ]
        )
    print(f'List of request values: {addon_details}')
    print(f'List of response values: {response_values}')
    # compare the request details list with the response details list
    return addon_details == response_values
