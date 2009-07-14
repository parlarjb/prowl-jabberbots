These are two bots I threw together to make use of the awesome Prowl app
for the iPhone [prowl.weks.net/](http://prowl.weks.net)

The first bot (monitor.py) registers a list of Jabber accounts to watch, and does a Push notification when those accounts go offline. This is useful if you use BeeJive, or IM+, or any iPhone IM client that boots you off their servers after a certain amount of time. This requires two text files. The first is 'monitor.txt'. Put the monitor account name on the first line (i.e. the new account you'll create to watch other accounts), and the password on the second line. Then, create another file called 'watchlist'. Each line in this file contains two things:

1. The account to watch (i.e. parlar@gmail.com)
2. The Prowl API key that should be notified when that account goes down

The second bot (emailnotify.py) logs into your GMail/GTalk account, and checks for new email. One nice feature is that not only can it notify you about email in your inbox, you can have it watch email in your various labels. Define a file 'labels.txt', with one label per line.

This bot also requires a text file, 'email.txt'. First line is your gmail address, second is your Gmail password, third is your Prowl API key

All of these require the 'prowlpy' library. I have my own version of this hosted at [http://github.com/parlarjb/prowlpy/tree/master](http://github.com/parlarjb/prowlpy/tree/master), which is based off of [http://github.com/jacobb/prowlpy/tree/master](http://github.com/jacobb/prowlpy/tree/master)

There are some standard third party libraries you'll need. [xmpppy](http://xmpppy.sourceforge.net/) and [httplib2](http://code.google.com/p/httplib2/) and [PyDNS](http://pydns.sourceforge.net/) Those are all installable with [pip](http://pypi.python.org/pypi/pip) 


jabberbot.py is a SLIGHTLY modified version of the source available [here](http://thpinfo.com/2007/python-jabberbot/)
