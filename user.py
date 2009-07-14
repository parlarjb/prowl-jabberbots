# user.py: Tracks user information, and creates a Prowl controller
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

import prowlpy

class User(object):
    def __init__(self, name, apikey):
        self.name = name
        self.apikey = apikey
        self.last_offline = "Haven't seen a disconnect yet"
        self.old_priority = -1
        self.prowl = prowlpy.Prowl(apikey)
