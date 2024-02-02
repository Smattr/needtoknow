'''
Functionality common to RSS-based feeders. This file is not intended to be
imported as a standalone feeder.
'''

import html

import feedparser


def get_feed(url, etag=None, modified=None):

    kwargs = {}
    if etag is not None:
        kwargs['etag'] = etag
    if modified is not None:
        kwargs['modified'] = modified

    response = feedparser.parse(url, **kwargs)

    if getattr(response, 'status', None) == 304: # “Not Modified”
        response.etag = etag
        response.modified = modified

    return response

def get_entries(response):
    if getattr(response, 'status', None) == 304:
      return []
    return response.entries

def get_id(entry):
    try:
        return entry.id
    except:
        return entry.title

def get_content(entry):
    try:
        return entry.content[0].value
    except:
        try:
            return entry.description
        except:
            return ''

def get_date(entry):
    try:
        return entry.updated_parsed
    except:
        return None

def get_links(entry):
    l = set()
    try:
        l.add(entry.link)
    except:
        pass
    try:
        for link in entry.links:
            l.add(link.url)
    except:
        pass
    return l

def get_title(entry):
    try:
        if entry.title_detail.type == 'text/html':
            return entry.title_detail.value
    except:
        pass
    return html.escape(entry.title)
