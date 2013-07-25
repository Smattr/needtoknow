import base
import feedparser

class Feeder(base.Feeder):
    def __iter__(self):
        for n, i in self.feeds.items():
            assert 'url' in i
            url = i['url']
            seen = self.resource.get(url, set())
            new = feedparser.parse(url)
            for e in new.entries:
                if e.id not in seen:
                    yield base.Entry(n, e.title, e.description, html=True)
                    seen.add(e.id)
            self.resource[url] = seen
