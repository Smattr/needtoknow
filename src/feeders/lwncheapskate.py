'''
Feeder for LWN that only notifies you when a page is available to
non-subscribers.
'''

from . import base, rsscommon
import urllib.request

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
                    try:
                        # See if the page is available.
                        urllib.request.urlopen(e.link)
                        # No 503 :)
                        yield base.Entry(n, e.title, rsscommon.get_content(e), html=True)
                        seen.add(id)
                    except:
                        # 503 :(
                        pass
            self.resource[url] = seen
