"""Simple URL parser that extracts components from URLs."""


def parse_url(url: str) -> dict:
    """Parse a URL string into its components.

    Returns a dict with keys: scheme, host, port, path, query, fragment.
    """
    if not url or not isinstance(url, str):
        return {"scheme": "", "host": "", "port": None, "path": "", "query": "", "fragment": ""}

    result = {"scheme": "", "host": "", "port": None, "path": "", "query": "", "fragment": ""}

    # Fragment
    if "#" in url:
        url, result["fragment"] = url.rsplit("#", 1)

    # Query
    if "?" in url:
        url, result["query"] = url.split("?", 1)

    # Scheme
    if "://" in url:
        result["scheme"], url = url.split("://", 1)

    # Host and path
    if "/" in url:
        result["host"], result["path"] = url.split("/", 1)
        result["path"] = "/" + result["path"]
    else:
        result["host"] = url

    # Port
    if ":" in result["host"]:
        result["host"], port_str = result["host"].rsplit(":", 1)
        try:
            result["port"] = int(port_str)
        except ValueError:
            pass

    return result


def normalize_url(url: str) -> str:
    """Normalize a URL by lowercasing scheme and host, removing default ports."""
    parts = parse_url(url)
    scheme = parts["scheme"].lower()
    host = parts["host"].lower()

    # Remove default ports
    port = parts["port"]
    if (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
        port = None

    result = f"{scheme}://{host}"
    if port:
        result += f":{port}"
    result += parts["path"] or "/"
    if parts["query"]:
        result += f"?{parts['query']}"
    if parts["fragment"]:
        result += f"#{parts['fragment']}"
    return result
