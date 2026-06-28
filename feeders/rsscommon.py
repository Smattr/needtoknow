"""
Functionality common to RSS-based feeders. This file is not intended to be
imported as a standalone feeder.
"""

import html
import re
from pathlib import Path
from typing import List, Optional, Union

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

    # XXX: Google Project Zero serves a feed that exceeds the default SAX parser limits
    # and claims to be ASCII but includes UTF-8 characters. Work around this by forcing
    # use of expat and UTF-8 interpretation.
    backend = feedparser.api.PREFERRED_XML_PARSERS
    if url == "https://projectzero.google/feed.xml":
        feedparser.api.PREFERRED_XML_PARSERS = ()
        kwargs["response_headers"] = {
            "content-type": "application/rss+xml; charset=UTF-8"
        }

    try:
        response = feedparser.parse(url, **kwargs)
    finally:
        feedparser.api.PREFERRED_XML_PARSERS = backend

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


def is_image(url: Union[Path, str]) -> bool:
    """is this link to an image?"""
    return Path(url).suffix.lower() in (".gif", ".jpeg", ".jpg", ".png", ".webp")


def get_links(entry, ignore_urls: Optional[List[str]] = None):
    if ignore_urls is None:
        ignore_urls = []
    l = []
    try:
        l += [entry.link]
    except:  # pylint: disable=bare-except
        pass
    try:
        l += [link.url for link in entry.links]
    except:  # pylint: disable=bare-except
        pass
    if len(l) > 1 and any(not is_image(u) for u in l):
        l = [u for u in l if not is_image(u)]
    return set(x for x in l if not any(re.search(r, x) for r in ignore_urls))


def get_title(entry):
    try:
        if entry.title_detail.type == "text/html":
            return entry.title_detail.value
    except:  # pylint: disable=bare-except
        pass
    return html.escape(entry.title)
