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

from setuptools import Command
from setuptools import setup

try:
	from setuptools.command.build import build
except ImportError:
	from distutils.command.build import build

NAME='syspeek'

class BuildDesktop(Command):
	description = "Builds desktop files"
	user_options = []

	def initialize_options(self):
		pass

	def finalize_options(self):
		pass

	def run(self):
		shutil.copy(os.path.join('data', NAME+'.desktop.in'), NAME+'.desktop')

build.sub_commands += [(x, lambda _: True) for x in ["build_desktop"]]

def list_icons(size, section):
	prefix = os.path.join('data', 'icons', size, section)
	return [os.path.join(prefix, i) for i in os.listdir(prefix)]

setup(
	name=NAME,
	version='0.4',
	license='GPL-3',
	author='Georg Schmidl',
	author_email='georg.schmidl@vicox.net',
	description='A system monitor indicator.',
	long_description='SysPeek is a system monitor indicator that displays CPU usage, memory usage, swap usage, disk usage and network traffic.',
	url='https://github.com/vicox/syspeek',
	data_files=[
		('share/icons/hicolor/scalable/status', list_icons('scalable', 'status')),
		('share/icons/hicolor/scalable/apps', list_icons('scalable', 'apps')),
		('share/applications', [NAME+'.desktop',]),
		('bin', [os.path.join('bin', NAME)]),
		('/etc/xdg/autostart', [NAME+'.desktop',]),
	],
	packages=['syspeek'],
	package_data={NAME: ['ui/*.ui']},
	cmdclass={'build_desktop': BuildDesktop},
)
