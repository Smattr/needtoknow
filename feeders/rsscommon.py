"""
Functionality common to RSS-based feeders. This file is not intended to be
imported as a standalone feeder.
"""

import html

import feedparser


def check(url: str, response) -> None:
    """validate response to a feed request"""

    if not response.get("bozo"):
        return

    # let a lack of Content-type header pass because we still get valid data we
    # can interpret
    # (hello https://yosefk.com/blog/feed)
    if isinstance(response["bozo_exception"], feedparser.NonXMLContentType):
        return

    # let character encoding mistakes pass because we still get valid data we
    # can interpret
    # (hello https://pwy.io/feed.xml)
    if isinstance(response["bozo_exception"], feedparser.CharacterEncodingOverride):
        return

    raise RuntimeError(f"{url} returned invalid XML: {response['bozo_exception']}")


def get_feed(url, etag=None, modified=None):

    kwargs = {}
    if etag is not None:
        kwargs["etag"] = etag
    if modified is not None:
        kwargs["modified"] = modified

    response = feedparser.parse(url, **kwargs)

    check(url, response)

    if getattr(response, "status", None) == 304:  # “Not Modified”
        response.etag = etag
        response.modified = modified

    return response


def get_entries(response):
    if getattr(response, "status", None) == 304:
        return []
    return response.entries


def get_id(entry):
    try:
        return entry.id
    except:  # pylint: disable=bare-except
        return entry.title


def get_content(entry):
    try:
        return entry.content[0].value
    except:  # pylint: disable=bare-except
        try:
            return entry.description
        except:  # pylint: disable=bare-except
            return ""


def get_date(entry):
    try:
        return entry.updated_parsed
    except:  # pylint: disable=bare-except
        return None


def get_links(entry):
    l = set()
    try:
        l.add(entry.link)
    except:  # pylint: disable=bare-except
        pass
    try:
        for link in entry.links:
            l.add(link.url)
    except:  # pylint: disable=bare-except
        pass
    return l


def get_title(entry):
    try:
        if entry.title_detail.type == "text/html":
            return entry.title_detail.value
    except:  # pylint: disable=bare-except
        pass
    return html.escape(entry.title)
