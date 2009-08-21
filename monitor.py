# monitordisconnects: Watch for disconnects in Jabber accounts
#
# Copyright (c) 2009 Jay Parlar <parlar@gmail.com>
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
import datetime
from user import User
from password import get_username_password_key

class GtalkMonitorJabberBot(JabberBot):

    def __init__(self, username, password, watch_list):
        super(GtalkMonitorJabberBot, self).__init__(username, password,server = "talk.google.com", port = 5222 )

        self.users = {}
        for name, apikey in watch_list:
            self.users[name] = User(name, apikey)
            self.users[name].email_notify_running = False
    
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
        return "I'm sorry Dave, I can't do that"

    def idle_proc(self):
        
        for name in self.users:
            priorities = []
            resources =  self.conn.getRoster().getRawRoster()[name]['resources']
            resource_names = resources.keys()
            for resource in resources:
                priorities.append(int(resources[resource]['priority']))
            try:
                highest = max(priorities)
            except ValueError:
                # priorities is empty, so they're not logged on anywhere
                disconnected = True
                highest = -1

            if highest != self.users[name].old_priority:
                self.users[name].old_priority = highest
                if highest < 0:
                    # Either the user is completely offline, 
                    # or the user is logged in, but only with emailnotify.py
                    print "Offline", name
                    self.users[name].last_offline = str(datetime.datetime.now())
                    try:
                        self.users[name].prowl.post("Disconnects", "Went Offline", "You went offline at %s." % self.users[name].last_offline)
                    except Exception, msg:
                        print msg

            email_notify_running = False
            for resource in resource_names:
                if resource.startswith(u"EmailNotif"):
                    email_notify_running = True
                    self.users[name].email_notify_running = True
                    break
            if not email_notify_running and self.users[name].email_notify_running:
                # Last time we checked, emailnotify was online, but now
                # it's offline
                try:
                    self.users[name].email_notify_running = False
                    self.users[name].prowl.post("Disconnects", "emailnotify.py", "Your emailnotify.py went offline at %s" % str(datetime.datetime.now())) 
                except Exception, msg:
                    print msg
            elif email_notify_running:
                self.users[name].email_notify_running = True



import os,sys
dirname = os.path.dirname(sys.argv[0])
monitorfile = os.path.join(dirname, "monitor.txt")
watchlist = os.path.join(dirname, "watchlist")
username, password, key = get_username_password_key(monitorfile) 
jid = username + "/jabb"

watch_list = []
f = open(watchlist)
for line in f:
    email, key = line.split()
    watch_list.append( (unicode(email), key))

bot = GtalkMonitorJabberBot(jid,password, watch_list)
bot.serve_forever()

