class Feeder(object):
    def __init__(self, resource):
        self.resource = resource
        self.items = []

    def add(self, item):
        self.items.append(item)

    def __iter__(self):
        raise NotImplementedError
