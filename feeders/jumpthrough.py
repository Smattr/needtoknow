import urllib.error

from . import base, rsscommon


class Feeder(base.Feeder):
    """an entry generator that produces the content of HTML pages"""
    def __iter__(self):
        for n, i in self.feeds.items():
            assert "url" in i
            url = i["url"]
            data = self.resource.get(url, {})
            if isinstance(data, dict):  # new scheme
                etag = data.get("etag")
                modified = data.get("modified")
                seen = data.get("seen", [])[:]
            else:  # old scheme
                assert isinstance(data, list)
                etag = None
                modified = None
                seen = data[:]
            try:
                feed = rsscommon.get_feed(url, etag, modified)
                entries = rsscommon.get_entries(feed)
                for e in entries:
                    ident = rsscommon.get_id(e)
                    if ident not in seen:
                        try:
                            data = base.download(e.link, self.log)
                            yield base.Entry(
                                n, e.title, data, date=rsscommon.get_date(e), html=True
                            )
                        except urllib.error.HTTPError:
                            # Suppress 404s from broken links.
                            pass
                        seen.append(ident)
                # save in new scheme
                self.resource[url] = {
                    "etag": etag,
                    "modified": modified,
                    "seen": seen,
                }
                yield base.SyncRequest()
            except Exception as e:
                yield Exception(f"Error from feed {n}: {e}")
