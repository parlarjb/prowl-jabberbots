

# emailnotify: Google email notification via Jabber
#
# Copyright (c) 2009 Jay Parlar <parlar@gmail.com>
#
# Portions of this code are *heavily* influenced by the Gajim 
# project, http://www.gajim.org/
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from jabberbot import JabberBot
import datetime, time
from user import User
import xmpp
from password import get_username_password_key


GMAILNOTIFY = 'google:mail:notify'

class EmailNotifyJabberBot(JabberBot):

    def __init__(self, username, password, apikey, labels = []):
        self._id = 1
        self.gmail_last_time = None
        self.gmail_last_tid = None
        self.waiting_for_result = False
        self.got_first_response = False
        self.last_id = self._id
        self.last_query_time = time.time()
        super(EmailNotifyJabberBot, self).__init__(username, password, server = "talk.google.com", port = 5222)
        
        self.user = User(username, apikey)

        labels.insert(0, "in:inbox")


        self.q = 'is:unread (' + " | ".join(labels) + ")"
        print self.q
   
    def _get_id(self):
        self._id += 1
        return str(self._id)
    id = property(_get_id)

    def bot_time( self, mess, args):
        """Displays current server time"""
        return str(datetime.datetime.now())

    def bot_rot13( self, mess, args):
        """Returns passed arguments rot13'ed"""
        return args.encode('rot13')

    def bot_whoami( self, mess, args):
        """Tells you your username"""
        return mess.getFrom()

    def bot_offline(self, mess, args):
        user= mess.getFrom().getStripped()
        return self.users[user].last_offline

    def unknown_command(self, mess, cmd, args):
        print "Got unknown message", args, mess.getFrom()
        return "This is an automated away message. I am currently not at a computer"

    def connect_callback(self):
        '''
        This tells Gmail that we want new mail notifications
        '''
        self.conn.send(xmpp.Presence(priority=-1, show='xa', status = "I'm currently unavailable, messages sent will not be received"))
        self.conn.RegisterHandler('iq', self._newMailCB, 'set', 
                                    GMAILNOTIFY)

        self.conn.RegisterHandler('iq', self._mailQueryCB, 'result',
                                    GMAILNOTIFY)


        iq = xmpp.Iq(typ='set', to=username)
        iq.setAttr('id','MailNotify')
        query = iq.setTag('usersetting')
        query.setNamespace('google:setting')
        query2 = query.setTag('mailnotifications')
        query2.setAttr('value', 'true')
        self.conn.send(iq)
        
        # Ask how many messages there are now
        self.send_email_query()
       

    def send_email_query(self):
        self.last_query_time = time.time()
        iq = xmpp.Iq(typ = 'get')
        id = self.id
        self.last_id = id
        self.waiting_for_result = True
        iq.setID(id)
        query = iq.setTag('query')
        query.setNamespace(GMAILNOTIFY)
        # we want only be notified about newer mails
        if self.gmail_last_tid:
            query.setAttr('newer-than-tid', self.gmail_last_tid)
        if self.gmail_last_time:
            query.setAttr('newer-than-time', self.gmail_last_time)
        query.setAttr('q', self.q)
        self.conn.send(iq)

    def idle_proc(self):
        if time.time() - self.last_query_time < 20:
            pass
        else:
            if self.gmail_last_time:
                self.gmail_last_time += 1
            self.send_email_query()

    def _newMailCB(self, conn, mess):
        id = mess.getAttr('id')
        to = mess.getAttr('to')
        frm = mess.getAttr('from')

        iq = xmpp.Iq(typ='result')
        iq.setAttr('to', to)
        iq.setAttr('from',frm)
        iq.setAttr('id', id)
        self.conn.send(iq)


        self.send_email_query()
       
  
    def _mailQueryCB(self, conn, mess):
        newmsgs = int(mess.getTag('mailbox').getAttr('total-matched'))
        if newmsgs != 0:
            # There are new messages
            print "New useable messages", mess.getAttr('id')
            self.waiting_for_result = False
            self.got_first_response = True
            gmail_messages_list = []
            if mess.getTag('mailbox').getTag('mail-thread-info'):
                gmail_messages = mess.getTag('mailbox').getTags('mail-thread-info')
                for gmessage in gmail_messages:
                    unread_senders = []
                    for sender in gmessage.getTag('senders').getTags('sender'):
                        if sender.getAttr('unread') != '1':
                            continue
                        if sender.getAttr('name'):
                            unread_senders.append(sender.getAttr('name') + ' < ' +\
                                    sender.getAttr('address') + '>')
                        else:
                            unread_senders.append(sender.getAttr('address'))
                    if not unread_senders:
                        continue
                    subject = gmessage.getTag('subject').getData()
                    snippet = gmessage.getTag('snippet').getData()
                    tid = int(gmessage.getAttr('tid'))
                    if not self.gmail_last_tid or tid > self.gmail_last_tid:
                        self.gmail_last_tid = tid
                    gmail_messages_list.append((unread_senders, subject, snippet))
                print "Result time", int(mess.getTag('mailbox').getAttr('result-time'))
                self.gmail_last_time = int(mess.getTag('mailbox').getAttr('result-time')) + 1    

                for unread_senders, subject, snippet in gmail_messages_list:
                    try:
                        #if snippet[-1] == u'\u2026':
                        #    snippet = snippet[:-1] + u"..."
                        self.user.prowl.post(u"Email", u"[" + unread_senders[0] + u"]" + subject, snippet)
                        print "Posted", unread_senders, subject, self.gmail_last_time, self.gmail_last_tid
                    except Exception, msg:
                        print "Got exception"
                        print msg
            else:
                print "No mail-thread-info"
                self.gmail_last_time = int(mess.getTag('mailbox').getAttr('result-time'))
import os
import sys
dirname = os.path.dirname(sys.argv[0])
emailfile = os.path.join(dirname, 'email.txt')
labelsfile = os.path.join(dirname,'labels.txt')
username, password, key = get_username_password_key(emailfile)
jid = username + "/jabb"

labels = []
if os.path.isfile(labelsfile):
    labels = []
    f = open(labelsfile)
    for line in f:
        labels.append( "label:"+line.strip().replace(" ", "-"))

bot = EmailNotifyJabberBot(jid,password, key, labels)
bot.serve_forever(bot.connect_callback)

