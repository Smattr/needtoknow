'''
Functionality common to RSS-based feeders. This file is not intended to be
imported as a standalone feeder.
'''

import feedparser

def get_entries(url):
    return feedparser.parse(url).entries

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
        map(lambda x: l.add(x.url), entry.links)
    except:
        pass
    return l
