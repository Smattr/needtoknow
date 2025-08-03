import abc
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional


class Feeder(abc.ABC):
    """
    common functionality for entry generators

    Args:
        resource: Feeder-specific data to persist between runs
        log: Sink for informational and debugging messages
        debug: Whether we are in debugging mode
    """
    def __init__(self, resource, log, debug: bool):
        self.resource = resource
        self.feeds = {}
        self.log = log
        self.debug = debug

    def add(self, name, item):
        self.feeds[name] = item

    @abc.abstractmethod
    def __iter__(self):
        raise NotImplementedError


@dataclass
class Entry:
    """
    an item yielded from a feed

    Args:
        name: The feeder this item originated from
        subject: Email subject to use when sending
        content: Body of the item
        date: Send date to use when sending
        html: Whether content is HTML or plain text
    """
    name: str
    subject: str
    content: str
    date: Optional[str] = None
    html: bool = False


def download(url, log):
    RETRIES = 3
    for i in range(RETRIES):
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                return response.read()
        except urllib.error.URLError as e:
            if i == RETRIES - 1:
                log.warning(f"download of {url} failed: {e}")
                raise
            log.warning(f"download of {url} failed (retrying): {e}")
            if getattr(e, "code", None) == 403:
                # Some sites explicitly block urllib to prevent crawling (e.g.
                # Microsoft). Since we're not really a crawler, sidestep this by
                # twiddling our user agent.
                request = urllib.request.Request(url, headers={"User-Agent": ""})
                with urllib.request.urlopen(request) as response:
                    return response.read()


class SyncRequest:
    """
    Sentinel class used by feeders to ask the main logic to write back state to disk.
    Feeders should use this following processing of each feed. The purpose of this is to
    minimise the resending of entries when a feeder is interrupted part way through.
    """
