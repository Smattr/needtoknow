class Feeder(object):
    def __init__(self, resource):
        self.resource = resource
        self.feeds = {}

    def add(self, name, item):
        self.feeds[name] = item

    def __iter__(self):
        raise NotImplementedError

class Entry(object):
    def __init__(self, name=None, subject=None, content=None, html=False):
        self.name = name or ''
        self.subject = subject or ''
        self.content = content or ''
        self.html = html
