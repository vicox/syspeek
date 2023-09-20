#!/usr/bin/env python3
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

import os
import sys
import shutil
import DistUtilsExtra.auto

NAME='syspeek'

class Install(DistUtilsExtra.auto.install_auto):
	def run(self):
		shutil.copy(os.path.join('data', NAME+'.desktop.in'), NAME+'.desktop')
		DistUtilsExtra.auto.install_auto.run(self)
		os.remove(NAME+'.desktop')

DistUtilsExtra.auto.setup(
	name=NAME,
	version='0.3',
	license='GPL-3',
	author='Georg Schmidl',
	author_email='georg.schmidl@vicox.net',
	description='A system monitor indicator.',
	long_description='SysPeek is a system monitor indicator that displays CPU usage, memory usage, swap usage, disk usage and network traffic.',
	url='http://launchpad.net/syspeek',
	data_files=[
		('/etc/xdg/autostart', [NAME+'.desktop',]),
	],
	package_data={NAME: ['ui/*.ui']},
	cmdclass={'install': Install},
)
