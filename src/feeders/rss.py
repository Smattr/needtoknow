import base, rsscommon

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
                            yield base.Entry(n, e.title, \
                               '<p><b>%(title)s</b><br/><font size="-1">%(links)s</font></p>%(content)s' % {
                                   'title':rsscommon.get_title(e),
                                   'links':'<br/>'.join(map(lambda x: '<a href="%(link)s">%(link)s</a>' % {'link':x}, links)),
                                   'content':rsscommon.get_content(e),
                               }, date=rsscommon.get_date(e), html=True)
                            seen.add(id)
                    except Exception as e:
                        yield Exception('Error from feed %(name)s: %(err)s' % {
                            'name':n,
                            'err':e,
                        })
                self.resource[url] = seen
            except Exception as e:
                yield Exception('Error from feed %(name)s: %(err)s' % {
                    'name':n,
                    'err':e,
                })
