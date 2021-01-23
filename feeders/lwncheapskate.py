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
            data = self.resource.get(url, {})
            if isinstance(data, dict): # new scheme
                etag = data.get('etag')
                modified = data.get('modified')
                seen = data.get('seen', [])[:]
            else: # old scheme
                assert isinstance(data, list)
                etag = None
                modified = None
                seen = data[:]
            feed = rsscommon.get_feed(url, etag, modified)
            entries = rsscommon.get_entries(feed)
            for e in entries:
                id = rsscommon.get_id(e)
                if id not in seen:
                    try:
                        # See if the page is available.
                        urllib.request.urlopen(e.link)
                        # No 503 :)
                        yield base.Entry(n, e.title, rsscommon.get_content(e), html=True)
                        seen.append(id)
                    except:
                        # 503 :(
                        pass
            # save in new scheme
            self.resource[url] = {
              'etag':etag,
              'modified':modified,
              'seen':seen,
            }
            yield base.SyncRequest()
