def is_htmx(request):
    """
    Check if the given request is an HTMX request by checking the 'HX-Request' header.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        bool: True if the request is an HTMX request, False otherwise.
    """

    return True if request.META.get('HTTP_HX_REQUEST') else False