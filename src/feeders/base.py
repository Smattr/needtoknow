import urllib2

class Feeder(object):
    def __init__(self, resource):
        self.resource = resource
        self.feeds = {}

    def add(self, name, item):
        self.feeds[name] = item

    def __iter__(self):
        raise NotImplementedError

class Entry(object):
    def __init__(self, name=None, subject=None, content=None, date=None, html=False, files=None):
        self.name = name or ''
        self.subject = subject or ''
        self.content = content or ''
        self.date = date
        self.html = html
        self.files = files or []

def download(url):
    RETRIES = 3
    for i in range(RETRIES):
        try:
            response = urllib2.urlopen(url)
            return response.read()
        except urllib2.URLError as e:
            if i == RETRIES - 1:
                raise
            if getattr(e, 'code', None) == 403:
                # Some sites explicitly block urllib2 to prevent crawling (e.g.
                # Microsoft). Since we're not really a crawler, sidestep this by
                # twiddling our user agent.
                request = urllib2.Request(url, headers={'User-Agent':''})
                response = urllib2.urlopen(request)
                return response.read()
