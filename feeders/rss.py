from . import base, rsscommon

class Feeder(base.Feeder):
    def __iter__(self):
        for n, i in self.feeds.items():
            assert 'url' in i
            url = i['url']
            seen = self.resource.get(url, set())
            try:
                entries = rsscommon.get_entries(url)
                for e in entries:
                    try:
                        id = rsscommon.get_id(e)
                        if id not in seen:
                            links = rsscommon.get_links(e)
                            yield base.Entry(n, e.title,
                               '<p><b>%(title)s</b><br/><font size="-1">%(links)s</font></p>%(content)s' % {
                                   'title':rsscommon.get_title(e),
                                   'links':'<br/>'.join(f'<a href="{x}">{x}</a>' for x in links),
                                   'content':rsscommon.get_content(e),
                               }, date=rsscommon.get_date(e), html=True)
                            seen.add(id)
                    except Exception as e:
                        yield Exception(f'Error from feed {n}: {e}')
                self.resource[url] = seen
                yield base.SyncRequest()
            except Exception as e:
                yield Exception(f'Error from feed {n}: {e}')
