#
#    Copyright (C) 2011  Georg Schmidl <georg.schmidl@vicox.net>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

NAME = 'syspeek'
DISPLAY_NAME = 'SysPeek'
COMMENTS = 'System Monitor Indicator'
VERSION = '0.3'
LICENSE = 'GPL-3'
COPYRIGHT = 'Copyright (C) 2011 Georg Schmidl'
WEBSITE = 'https://launchpad.net/syspeek'

AUTHORS = [
	'Georg Schmidl <georg.schmidl@vicox.net>',
	'Marco Trevisan <mail@3v1n0.net>'
]

LICENSE_TEXT = \
'''This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.'''

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gtk
from syspeek.indicator import *

def main():
	# Workaround to python gtk bug (#622084) causing Ctrl+C not to work
	import signal
	signal.signal(signal.SIGINT, signal.SIG_DFL)

	syspeek = SysPeekIndicator()
	Gtk.main()
