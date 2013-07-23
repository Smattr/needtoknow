class Feeder(object):
    def __init__(self, resource):
        self.resource = resource
        self.feeds = {}

    def add(self, name, item):
        self.feeds[name] = item

    def __iter__(self):
        raise NotImplementedError
