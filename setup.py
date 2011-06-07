#!/usr/bin/env python
#
#    SysPeek is a system monitor indicator that displays system information
#    like CPU usage, memory usage, swap usage, etc.
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

import DistUtilsExtra.auto

DistUtilsExtra.auto.setup(
	name='syspeek',
	version='0.1',
	license='GPL-3',
	author='Georg Schmidl',
	author_email='georg.schmidl@vicox.net',
	description='A system monitor indicator.',
	long_description='SysPeek is a system monitor indicator that displays CPU usage, memory usage, swap usage, disk usage and network traffic.',
	url='http://launchpad.net/syspeek',
	data_files=[
		('/usr/local/share/gnome/autostart', ['autostart/syspeek.desktop',]),
	],
)
