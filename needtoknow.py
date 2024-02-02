#!/usr/bin/env python3

import argparse
import bz2
import collections
import fcntl
import importlib
import json
import logging
import numbers
import pickle
import re
import socket
import sys
import urllib.error
import urllib.request
from pathlib import Path

from feeders.base import SyncRequest
from output import sender

# How many times to attempt reconnecting to our output mailbox when the
# connection is dropped.
RECONNECT_ATTEMPTS = 3


def get_resource_path(root: str, name: str) -> Path:
    return Path(root) / f"cache/{name}.pickle.bz2"


def construct_feeder(root, name, log):
    try:
        mod = importlib.import_module(f"feeders.{name}")
    except Exception as e:
        log.warning(f"failed to import feeder {name}: {e}")
        return None

    respath = get_resource_path(root, name)
    if respath.exists():
        with bz2.open(respath, "rb") as f:
            resource = pickle.load(f)
    else:
        resource = {}

    return mod.Feeder(resource)


def online():
    try:
        urllib.request.urlopen("http://www.google.com", timeout=5)
        return True
    except urllib.error.URLError:
        return False


def main():
    parser = argparse.ArgumentParser("Monitor RSS and other feeds")
    parser.add_argument(
        "--disable",
        "-d",
        action="append",
        default=[],
        help="disable a particular feeder by name",
    )
    parser.add_argument(
        "--enable",
        "-e",
        action="append",
        default=[],
        help="enable a particular feeder by name",
    )
    parser.add_argument(
        "--exclude",
        "-x",
        action="append",
        default=[],
        help="exclude a particular feed by name",
    )
    parser.add_argument(
        "--include",
        "-i",
        action="append",
        default=[],
        help="include a particular feed by name",
    )
    parser.add_argument(
        "--check-connection",
        action="store_true",
        help="check whether we have an internet connection first",
    )
    parser.add_argument(
        "--config",
        default=str(Path("~/.needtoknow").expanduser()),
        help="configuration location",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="scan feeds but don't send any updates"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="instead of catching exceptions, let them dump a back trace",
    )
    opts = parser.parse_args()

    log = logging.getLogger("needtoknow")
    log.addHandler(logging.StreamHandler(sys.stderr))
    # Determine whether we are running interactively.
    if sys.stdout.isatty():
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.WARNING)

    # Check whether we're already running, to prevent multiple instances running
    # at once. Multiple running instances can interfere with each other when
    # saving state.
    me = open(Path(__file__).resolve(), "rt")
    try:
        fcntl.flock(me, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        log.error("needtoknow is already running; exiting\n")
        return -1

    if opts.check_connection and not online():
        log.info("no network connection; exiting")
        return 0

    try:
        with open(Path(opts.config) / "conf.json", "rt", encoding="utf-8") as f:
            conf = json.load(f)
        if not isinstance(conf, collections.abc.Mapping):
            raise TypeError("configuration is not a JSON object")
        if not all(isinstance(v, (str, numbers.Integral)) for v in conf.values()):
            raise TypeError("configuration values are not all strings or numbers")
    except Exception as e:
        if opts.debug:
            raise
        log.error(f"Failed to parse config: {e}")
        return -1

    try:
        with open(Path(opts.config) / "feeds.json", "rt", encoding="utf-8") as f:
            feeds = json.load(f)
        if not isinstance(feeds, collections.abc.Mapping):
            raise TypeError("feeds is not a JSON object")
        if not all(isinstance(v, collections.abc.Mapping) for v in feeds.values()):
            raise TypeError("feed values are not all JSON objects")
    except Exception as e:
        if opts.debug:
            raise
        log.error(f"Failed to parse feeds: {e}")
        return -1

    feeders = {}

    log.info("Loading feeders...")
    for s, v in feeds.items():
        f = v.get("feeder")
        if f not in feeders:
            log.info(f" Loading {f}...")
            feeders[f] = construct_feeder(opts.config, f, log)

        if feeders[f] is None:
            log.warning(f" Warning: No feeder named {f} (referenced by {s}).")
        else:
            if s in opts.include or (opts.include == [] and s not in opts.exclude):
                feeders[f].add(s, v)

    # Set timeout on socket connections to 60 seconds. Without this, some
    # platforms have no timeout (even on the kernel side) and socket connections
    # can stall forever.
    socket.setdefaulttimeout(60)

    out = sender.Sender(conf)
    try:
        out.connect()
    except Exception as e:
        if opts.debug:
            raise
        log.error(f"Failed to connect to mail server: {e}")
        return -1

    ret = 0

    log.info("Looking for updates...")
    for f in feeders:

        def commit_changes():
            if not opts.dry_run:
                log.info("  Committing resource changes...")
                respath = get_resource_path(opts.config, f)
                respath.parent.mkdir(exist_ok=True)
                tmp = Path(f"{respath}.tmp")
                with bz2.open(tmp, "wb") as fobj:
                    pickle.dump(feeders[f].resource, fobj)
                tmp.rename(respath)

        if feeders[f] is None:
            # We failed to load this feeder.
            continue
        if f in opts.disable or (opts.enable != [] and f not in opts.enable):
            continue
        try:
            log.info(f" Scanning {f}...")
            for entry in feeders[f]:

                if isinstance(entry, Exception):
                    if opts.debug:
                        raise entry
                    log.warning(f"  Feeder '{f}' threw exception: {entry}")
                    ret = -1
                    continue
                elif isinstance(entry, SyncRequest):
                    commit_changes()
                    continue

                # Check if we should discard this entry.
                assert (
                    entry.name in feeders[f].feeds
                ), f"feeder '{f}' yielded entry from unknown feed '{entry.name}'"
                skip = False
                for blocklist in feeders[f].feeds[entry.name].get("blocklist", []):
                    try:
                        if re.search(blocklist, entry.subject) is not None:
                            log.info(
                                f"  Discarding '[{entry.name}] {entry.subject}' as blocklisted"
                            )
                            skip = True
                            break
                    except Exception as e:
                        if opts.debug:
                            raise
                        log.error(
                            f"  Failed to run regex blocklist '{blocklist}' "
                            "against {entry.name}: {e}"
                        )
                        ret = -1
                if skip:
                    continue
                if opts.dry_run:
                    log.info(f"  skipping '{entry.subject}' send due to --dry-run")
                    continue
                try:
                    for i in range(RECONNECT_ATTEMPTS + 1):
                        try:
                            out.send(entry, log, i == 0)
                            break
                        except ConnectionResetError:
                            if i == RECONNECT_ATTEMPTS:
                                raise
                            log.info("  connection reset by peer; reconnecting...")
                        except (socket.timeout, TimeoutError):
                            if i == RECONNECT_ATTEMPTS:
                                raise
                            log.info("  socket timeout; reconnecting...")
                        out.connect()
                except Exception as e:
                    if opts.debug:
                        raise
                    log.error(
                        f"  Failed to send update for {entry.name} '{entry.subject}': {e}"
                    )
                    ret = -1
        except Exception as e:
            if opts.debug:
                raise
            log.warning(f"  Feeder '{f}' threw exception: {e}")

        commit_changes()

    out.disconnect()

    return ret


if __name__ == "__main__":
    sys.exit(main())
