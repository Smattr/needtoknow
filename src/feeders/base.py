class Feeder(object):
    def __init__(self, resource, **kwargs):
        self.resource = resource
        self.kwargs = kwargs

    def __iter__(self):
        raise NotImplementedError
