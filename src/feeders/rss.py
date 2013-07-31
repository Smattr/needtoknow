import base, rsscommon

class Feeder(base.Feeder):
    def __iter__(self):
        for n, i in self.feeds.items():
            assert 'url' in i
            url = i['url']
            seen = self.resource.get(url, set())
            entries = rsscommon.get_entries(url)
            for e in entries:
                id = rsscommon.get_id(e)
                if id not in seen:
                    yield base.Entry(n, e.title, rsscommon.get_content(e), html=True)
                    seen.add(id)
            self.resource[url] = seen
