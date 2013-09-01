import base, rsscommon
import urllib2

class Feeder(base.Feeder):
    def __iter__(self):
        for n, i in self.feeds.items():
            assert 'url' in i
            url = i['url']
            seen = self.resource.get(url, set())
            try:
                entries = rsscommon.get_entries(url)
                for e in entries:
                    id = rsscommon.get_id(e)
                    if id not in seen:
                        try:
                            resp = urllib2.urlopen(e.link)
                            yield base.Entry(n, e.title, \
                                resp.read(), \
                                date=rsscommon.get_date(e), \
                                html=True)
                        except urllib2.HTTPError:
                            # Suppress 404s from broken links.
                            pass
                        seen.add(id)
                self.resource[url] = seen
            except Exception as e:
                raise Exception('Error from feed %(name)s: %(err)s' % {
                    'name':n,
                    'err':e,
                })
