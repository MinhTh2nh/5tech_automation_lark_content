async def handle_route(route):
    """Block ads and unwanted requests."""
    blocked_patterns = ['ads', 'doubleclick.net', 'googlesyndication.com']
    if any(pattern in route.request.url for pattern in blocked_patterns):
        await route.abort()
    else:
        await route.continue_()
