Once upon a time...
===================
I was a happy `Google Reader`_ user. Then Google decided to kill it off because
it wasn't making them enough cash. From there, I bounced to Feedly_,
Blogtrottr_, rss2email_ and a bunch of others in-between. Much like Goldilocks,
nothing was quite right for me. I boiled my requirements down to a minimal list:

* RSS to email gateway. I need to heavily filter some feeds so why not make use
  of email filters that are more powerful than most feed-level filtering
  options?
* SMTP_ output. I am sick of messing with MTAs_ to get my local mail forwarded
  to an inbox I actually read. Actually this subsequently evolved into IMAP_
  output when I realised I could evade some unhelpful non-optional spam
  filtering by directly copying entries into a mailbox over IMAP.
* Text file configuration that I can check-in to `my utils repo`_. I don't like
  losing these things when my disk crashes.
* Easily extensible. I had some ideas for RSS-like monitoring of non-RSS
  sources.

.. _Blogtrottr: http://blogtrottr.com
.. _Feedly: http://www.feedly.com/
.. _`Google Reader`: http://www.google.com/reader
.. _IMAP: https://en.wikipedia.org/wiki/Internet_Message_Access_Protocol
.. _MTAs: https://en.wikipedia.org/wiki/Message_transfer_agent
.. _`my utils repo`: https://github.com/Smattr/mattutils
.. _rss2email: http://www.allthingsrss.com/rss2email/
.. _SMTP: https://en.wikipedia.org/wiki/Simple_Mail_Transfer_Protocol

What you see is my attempt to solve this with some scripting. It's a pretty
small codebase and (IMHO) pretty easily extensible via the feeders. Be aware it
is currently in no way polished and lacks even basic error handling.

Dependencies
------------

* Python 3 (sorry, no Python 2 compatibility)
* BeautifulSoup_
* feedparser_

.. _BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/
.. _feedparser: https://pythonhosted.org/feedparser/

Configuration
-------------
Needtoknow expects two configuration files provided to it as JSON_:

* ``conf.json``: How to access your mailbox.
* ``feeds.json``: What feeds to monitor.

.. _JSON: https://www.json.org/

By default, it looks for these files in the directory ``~/.needtoknow``. You can
specify a different directory with the ``--config`` command line option.

conf.json
^^^^^^^^^
The mailbox configuration file is expected to contain a dictionary detailing how
to connect to your mailbox:

.. code-block:: json

    {
      "host":"imap.gmail.com",
      "login":"example@gmail.com",
      "password":"correct horse battery staple"
    }

Note that your password is in *clear text in this file*. You should make efforts
to locate this file in a secure area or otherwise prevent access to it by
unauthorised users.

Only SSL_ connections are supported and the port to use defaults to 993. If you
need to override the default port, you can add an extra entry to the dictionary:

.. _SSL: https://en.wikipedia.org/wiki/Transport_Layer_Security

.. code-block:: json

    {
      "host":"imap.gmail.com",
      "login":"example@gmail.com",
      "password":"correct horse battery staple",
      "port":"42"
    }

By default, the above will result in new items being posted to your IMAP inbox.
If you want feed items to be posted to a different mailbox folder, you can
specify this as another dictionary entry:

.. code-block:: json

    {
      "host":"imap.gmail.com",
      "login":"example@gmail.com",
      "password":"correct horse battery staple",
      "folder":"my-feeds"
    }

Note that this folder must already exist.

feeds.json
^^^^^^^^^^
The feeds you want to monitor are provided as a dictionary, wherein each entry
represents a single feed. The mandatory elements to define for a feed are its
name, the "feeder" to use and its URL_:

.. _URL: https://en.wikipedia.org/wiki/URL

.. code-block:: json

    {
      "Hacker News":{
        "feeder":"rss",
        "url":"https://news.ycombinator.com/rss"
      },
      "Slashdot":{
        "feeder":"rss",
        "url":"http://rss.slashdot.org/Slashdot/slashdot"
      }
    }

The feeder defines the type of the feed and how to present its contents. For a
list of feeders, look under the directory src/feeders/. Several feeders have
their own options that can be tweaked via further dictionary entries. A full
explanation of each feeder and its features is beyond the scope of this README
and you will have to read their source to understand their capabilities.

Feed items will show up in your mailbox as emails from the name you have given
them in your ``feeds.json``. Perhaps you wish items from a specific feed to
appear as if they were sent by a person. You can achieve this by naming the feed
with a format representing a name and email address:

.. code-block:: json

    {
      "Paul Graham <p.g@ycombinator.com>":{
        "feeder":"rss",
        "url":"http://www.aaronsw.com/2002/feeds/pgessays.rss"
      }
    }

The advantage of this is that your mail client recognises this and will let you
naturally send a reply based on items from this feed to that person. [#]_

This is barely scratching the surface of what is possible with different feeders
and their configuration options, so as mentioned above please read their source
to learn more.

Scheduling
^^^^^^^^^^
Once you have needtoknow configured, you probably want to run it on a schedule.
You can do this with cron_ or your favourite scheduling utility. Note that
needtoknow outputs diagnostics and errors to stderr, so if you are using cron
any errors will be delivered to your local system mailbox. More detailed
information is emitted if stderr is a TTY_ because needtoknow thinks a human is
paying attention, so it can be helpful to configure your cron environment with
a pseudo TTY if you are debugging something.

.. _cron: https://en.wikipedia.org/wiki/Cron
.. _TTY: https://en.wikipedia.org/wiki/Computer_terminal#Text_terminals

Hacking
-------
Want to modify this code? Fork away. If you have any questions, let me know. If
you want a feature, but are too lazy to implement it yourself, ask me when I'm
having a good day and I may do it for you :)

Legal stuffs
------------
All files in this repository are in the public domain. Use them in any way you
wish. However, be aware that they come with no warranty. If you reuse this code,
I assume you will read and understand it first.

.. [#] If you actually do this with Paul Graham, I highly doubt he will answer
   your email.

