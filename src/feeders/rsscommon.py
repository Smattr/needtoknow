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
        return entry.date
    except:
        return None

def get_extra_link(entry):
    # Some RSS feeds have more than one link.
    try:
        return entry.links[1].url
    except:
        return ''
