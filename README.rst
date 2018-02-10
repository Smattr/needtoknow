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

Hacking
-------
Want to modify this code? Fork away. If you have any questions, let me know. If
you want a feature, but are too lazy to implement it yourself, ask me when I'm
having a good day and I may do it for you :)

Legal stuffs
------------
All files in this repository are licensed under a Creative Commons
Attribution-NonCommercial 3.0 Unported. You are free to reuse any of this code
for any non-commercial purpose. For more information see
https://creativecommons.org/licenses/by-nc/3.0/.
