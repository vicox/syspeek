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
import threading
import time
import traceback
from gi.repository import GObject as gobject
from abc import ABCMeta, abstractmethod

class Supplier(threading.Thread):
	__metaclass__ = ABCMeta

	def __init__(self, display, interval=1):
		threading.Thread.__init__(self)
		self.display = display
		self.interval = interval
		self._stop = threading.Event()
		self.setDaemon(True)

	def run(self):
		self.running = True
		while not self.stopped():
			try:
				self.supply()
			except:
				traceback.print_exc()
			time.sleep(self.interval)

	def stop(self):
		self._stop.set()

	def stopped(self):
		return self._stop.isSet()

	@abstractmethod
	def supply(self): pass

class CpuSupplier(Supplier):
	last_total = {}
	last_busy = {}

	supply_average = False
	supply_cores = False

	IDLE = 3

	def get_cpu_count(self):
		f = open('/proc/stat', 'r')
		stat = f.readlines()
		f.close()

		count = -1
		for line in stat:
			if line.startswith('cpu'):
				count = count + 1
			else:
				break
		return count

	def calculate_percentage(self, stats, core):
		total = sum(stats)
		busy = total - stats[self.IDLE]

		if core not in self.last_total:
			self.last_total[core] = 0
		if core not in self.last_busy:
			self.last_busy[core] = 0

		delta_total = total - self.last_total[core]
		delta_busy = busy - self.last_busy[core]

		percentage = 0
		if delta_total > 0 and delta_busy > 0:
			percentage = (float(delta_busy) / delta_total) * 100

		self.last_total[core] = total
		self.last_busy[core] = busy

		return percentage

	def supply(self):
		f = open('/proc/stat', 'r')
		stat = f.readlines()
		f.close()

		percentages = []
		for core in range(len(stat)):
			if stat[core].startswith('cpu'):
				stats= [int(x) for x in stat[core].split()[1:8]]
				percentages.append(self.calculate_percentage(stats, core))
				if core == 0 and not self.supply_cores:
					break
			else:
				break

		if self.supply_average:
			gobject.idle_add(self.display.update_cpu, percentages[0])

		if self.supply_cores:
			gobject.idle_add(self.display.update_cpu_cores, percentages[1:])

class MemSwapSupplier(Supplier):
	def supply(self):
		meminfo = {}

		f = open('/proc/meminfo', 'r')
		lines = f.readlines()
		f.close()

		for line in lines:
			row = line.split()
			if row[0] in ['MemTotal:', 'MemFree:', 'Buffers:', 'Cached:', 'SwapTotal:', 'SwapFree:']:
				meminfo[row[0][0:len(row[0]) - 1]] = int(row[1]) * 1024

		mem_used = meminfo['MemTotal'] - meminfo['MemFree'] - meminfo['Buffers'] - meminfo['Cached']
		swap_used = meminfo['SwapTotal'] - meminfo['SwapFree']
		
		gobject.idle_add(self.display.update_memswap,
			mem_used,
			meminfo['MemTotal'],
			swap_used,
			meminfo['SwapTotal']
		)

class NetworkSupplier(Supplier):
	last_receive = 0
	last_transmit = 0

	FLAGS = 3
	UG = '0003'
	ROUTE_INTERFACE = 0
	DEV_INTERFACE = 0
	RECEIVE = 1
	TRANSMIT = 9

	def supply(self):
		interface = self.active_interface()
		receive = 0
		transmit = 0
		if interface is not None:
			f = open('/proc/net/dev', 'r')
			lines = f.readlines()
			f.close()

			for line in lines:
				row = line.split()
				if row[self.DEV_INTERFACE] == interface + ':':
					receive = int(row[self.RECEIVE])
					transmit = int(row[self.TRANSMIT])

		delta_receive = receive - self.last_receive
		delta_transmit = transmit - self.last_transmit

		gobject.idle_add(self.display.update_network,
			int(delta_receive / self.interval),
			int(delta_transmit / self.interval),
			receive,
			transmit
		)

		self.last_receive = receive
		self.last_transmit = transmit
					

	def active_interface(self):
		f = open('/proc/net/route', 'r')
		lines = f.readlines()
		f.close()

		for line in lines:
			row = line.split()
			if row[self.FLAGS] == self.UG:
				return row[self.ROUTE_INTERFACE]

class DiskSupplier(Supplier):
	directories = []

	def supply(self):
		values = {}
		for directory in self.directories:
			try:
				stat = os.statvfs(directory)
				values[directory] = {}
				values[directory]['total'] = stat.f_bsize * stat.f_blocks
				values[directory]['used'] = (
					values[directory]['total'] - (stat.f_bsize * stat.f_bfree)
				)
			except:
				print "ERROR: Could not get data for " + directory

		gobject.idle_add(self.display.update_disk, values)

