# Once upon a time...

I was a happy [Google Reader](http://www.google.com/reader) user. Then Google
decided to kill it off because it wasn't making them enough cash. From there, I
bounced to [Feedly](http://www.feedly.com/),
[Blogtrottr](http://blogtrottr.com),
[rss2email](http://www.allthingsrss.com/rss2email/) and a bunch of others
in-between. Much like Goldilocks, nothing was quite right for me. I boiled my
requirements down to a minimal list:

* RSS to email gateway. I need to heavily filter some feeds so why not make use
  of email filters that are more powerful than most feed-level filtering
  options?
* [SMTP](https://en.wikipedia.org/wiki/Simple_Mail_Transfer_Protocol) output. I
  am sick of messing with
  [MTAs](https://en.wikipedia.org/wiki/Message_transfer_agent) to get my local
  mail forwarded to an inbox I actually read.
* Text file configuration that I can check-in to
  [my utils repo](https://github.com/Smattr/mattutils). I don't like losing
  these things when my disk crashes.
* Easily extensible. I had some ideas for RSS-like monitoring of non-RSS
  sources.

What you see is my attempt to solve this with some scripting. It's a pretty
small codebase and (IMHO) pretty easily extensible via the feeders. Be aware it
is currently in no way polished and lacks even basic error handling.

# Dependencies

* Python 3 (sorry, no Python 2 compatibility)
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
* [feedparser](https://pythonhosted.org/feedparser/)

# Hacking

Want to modify this code? Fork away. If you have any questions, let me know. If
you want a feature, but are too lazy to implement it yourself, ask me when I'm
having a good day and I may do it for you :)

# Legal stuffs

All files in this repository are licensed under a Creative Commons
Attribution-NonCommercial 3.0 Unported. You are free to reuse any of this code
for any non-commercial purpose. For more information see
[https://creativecommons.org/licenses/by-nc/3.0/](https://creativecommons.org/licenses/by-nc/3.0/).
