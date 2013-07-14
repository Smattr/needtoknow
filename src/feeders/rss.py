import base

class Feeder(base.Feeder):
    def __iter__(self):
        yield 'hello'
        yield 'world'
