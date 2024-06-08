from . import base, rsscommon


class Feeder(base.Feeder):
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
                    try:
                        id = rsscommon.get_id(e)
                        if id not in seen:
                            links = rsscommon.get_links(e)
                            yield base.Entry(
                                n,
                                e.title,
                                '<p><b>%(title)s</b><br/><font size="-1">%(links)s</font></p>%(content)s'
                                % {
                                    "title": rsscommon.get_title(e),
                                    "links": "<br/>".join(
                                        f'<a href="{x}">{x}</a>' for x in links
                                    ),
                                    "content": rsscommon.get_content(e),
                                },
                                date=rsscommon.get_date(e),
                                html=True,
                            )
                            seen.append(id)
                    except Exception as e:
                        yield Exception(f"Error from feed {n}: {e}")
                # save in new scheme
                etag = getattr(feed, "etag", etag)
                modified = getattr(feed, "modified", modified)
                self.resource[url] = {
                    "etag": etag,
                    "modified": modified,
                    "seen": seen,
                }
                yield base.SyncRequest()
            except Exception as e:
                yield Exception(f"Error from feed {n}: {e}")
