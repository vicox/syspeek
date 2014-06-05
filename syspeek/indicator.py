# -*- coding: utf-8 -*-
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
from gettext import gettext as _
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Gtk as gtk
from gi.repository import GObject as gobject
from gi.repository import GLib
import json
import pkg_resources

try:
	from UserDict import UserDict
except ImportError:
	from collections import UserDict

from syspeek import *
from syspeek.supplier import *
from syspeek.helper import human_readable as _h

class SysPeekIndicator():
	menu_items = {}
	suppliers = {}
	active_suppliers = []

	LABEL_CPU = _('CPU') + ': {0:.1f}%'
	LABEL_CORE = _('CPU') + '{0}: {1:.1f}%'
	LABEL_CORES = _('CPU') + '{0}: {1:.1f}%' + '    ' + _('CPU') + '{2}: {3:.1f}%'
	LABEL_MEMORY = _('Memory') + ': {0} ' + _('of') + ' {1}'
	LABEL_SWAP = _('Swap') + ': {0} ' + _('of') + ' {1}'
	LABEL_DISK = '{0}: {1} ' + _('of') + ' {2}'
	LABEL_RECEIVING = _('Receiving') + ': {0}/s'
	LABEL_SENDING = _('Sending') + ': {0}/s'
	LABEL_RECEIVED = _('Total Received') + ': {0}'
	LABEL_SENT = _('Total Sent') + ': {0}'

	LABEL_WAITING = _('Waiting for data') + '…'

	def __init__(self):
		self.indicator = appindicator.Indicator.new(NAME, NAME + '-0',
			appindicator.IndicatorCategory.HARDWARE
		)

		# in case app is running from local folder
		icon_path = os.path.abspath(os.path.join(
			os.path.dirname(__file__), '../data/icons/22x22/status')
		)
		if os.path.exists(icon_path):
			self.indicator.set_icon_theme_path(icon_path)

		self.indicator.set_status((appindicator.IndicatorStatus.ACTIVE))

		self.preferences = Preferences()
		self.preferences.load()

		self.suppliers['cpu'] = CpuSupplier(self)
		self.suppliers['memswap'] = MemSwapSupplier(self)
		self.suppliers['disk'] = DiskSupplier(self)
		self.suppliers['network'] = NetworkSupplier(self)

		self.build_menu()
		self.start_suppliers()

	def start_suppliers(self):
		if self.preferences['display_cpu_average']:
				self.suppliers['cpu'].supply_average = True

		if self.preferences['display_cpu_cores']:
				self.suppliers['cpu'].supply_cores = True

		if self.preferences['display_cpu_average'] or self.preferences['display_cpu_cores']:
			self.suppliers['cpu'].interval = self.preferences['update_interval_cpu']
			self.suppliers['cpu'].run()
		else:
			self.suppliers['cpu'].stop()

		if self.preferences['display_memory'] or self.preferences['display_swap']:
			self.suppliers['memswap'].interval = self.preferences['update_interval_memswap']
			self.suppliers['memswap'].run()
		else:
			self.suppliers['memswap'].stop()

		if self.preferences['display_disk'] and len(self.preferences['disks']) > 0:
			self.suppliers['disk'].interval = self.preferences['update_interval_disk']
			self.suppliers['disk'].directories = self.preferences['disks']
			self.suppliers['disk'].run()
		else:
			self.suppliers['disk'].stop()

		if self.preferences['display_network_speed'] or self.preferences['display_network_total']:
			self.suppliers['network'].interval = self.preferences['update_interval_network']
			self.suppliers['network'].run()
		else:
			self.suppliers['network'].stop()

	def build_menu(self):
		menu = gtk.Menu()

		system_monitor = gtk.MenuItem(_('System Monitor') + '…')
		system_monitor.connect('activate', self.system_monitor)
		system_monitor.show()
		menu.append(system_monitor)
		self.indicator.set_secondary_activate_target(system_monitor)

		system_monitor_separator = gtk.SeparatorMenuItem()
		menu.append(system_monitor_separator)
		system_monitor_separator.show()

		if self.preferences['display_cpu_average']:
			self.menu_items['cpu'] = gtk.MenuItem(self.LABEL_WAITING)
			menu.append(self.menu_items['cpu'])
			self.menu_items['cpu'].show()

		if self.preferences['display_cpu_cores']:
			cpu_count = self.suppliers['cpu'].get_cpu_count()
			self.menu_items['cores'] = {}
			for x in range(cpu_count / 2 + cpu_count % 2):
				self.menu_items['cores'][x] = gtk.MenuItem(self.LABEL_WAITING)
				menu.append(self.menu_items['cores'][x])
				self.menu_items['cores'][x].show()

		if self.preferences['display_cpu_average'] or self.preferences['display_cpu_cores']:
			self.menu_items['separator_cpu'] = gtk.SeparatorMenuItem()
			menu.append(self.menu_items['separator_cpu'])
			self.menu_items['separator_cpu'].show()

		if self.preferences['display_memory']:
			self.menu_items['memory'] = gtk.MenuItem(self.LABEL_WAITING)
			menu.append(self.menu_items['memory'])
			self.menu_items['memory'].show()

		if self.preferences['display_swap']:
			self.menu_items['swap'] = gtk.MenuItem(self.LABEL_WAITING)
			menu.append(self.menu_items['swap'])
			self.menu_items['swap'].show()

		if self.preferences['display_memory'] or self.preferences['display_swap']:
			self.menu_items['separator_memswap'] = gtk.SeparatorMenuItem()
			menu.append(self.menu_items['separator_memswap'])
			self.menu_items['separator_memswap'].show()

		if self.preferences['display_disk'] and len(self.preferences['disks']) > 0:
			self.menu_items['disks'] = {}
			for key in self.preferences['disks']:
				self.menu_items['disks'][key] = gtk.MenuItem(self.LABEL_WAITING)
				menu.append(self.menu_items['disks'][key])
				self.menu_items['disks'][key].show()

			self.menu_items['separator_disk'] = gtk.SeparatorMenuItem()
			menu.append(self.menu_items['separator_disk'])
			self.menu_items['separator_disk'].show()

		if self.preferences['display_network_speed']:
			self.menu_items['receiving'] = gtk.MenuItem(self.LABEL_WAITING)
			menu.append(self.menu_items['receiving'])
			self.menu_items['receiving'].show()

			self.menu_items['sending'] = gtk.MenuItem(self.LABEL_WAITING)
			menu.append(self.menu_items['sending'])
			self.menu_items['sending'].show()

		if self.preferences['display_network_total']:
			self.menu_items['received'] = gtk.MenuItem(self.LABEL_WAITING)
			menu.append(self.menu_items['received'])
			self.menu_items['received'].show()

			self.menu_items['sent'] = gtk.MenuItem(self.LABEL_WAITING)
			menu.append(self.menu_items['sent'])
			self.menu_items['sent'].show()

		if self.preferences['display_network_speed'] or self.preferences['display_network_total']:
			self.menu_items['separator_network'] = gtk.SeparatorMenuItem()
			menu.append(self.menu_items['separator_network'])
			self.menu_items['separator_network'].show()

		preferences_menu_item = gtk.MenuItem(_('Preferences'))
		preferences_menu_item.connect('activate', self.preferences_dialog)
		preferences_menu_item.show()
		menu.append(preferences_menu_item)

		about = gtk.MenuItem(_('About'))
		about.connect('activate', self.about)
		about.show()
		menu.append(about)

		quit = gtk.MenuItem(_('Quit'))
		quit.connect('activate', self.quit)
		quit.show()
		menu.append(quit)

		self.indicator.set_menu(menu)

	def update_cpu(self, percentage):
		self.indicator.set_icon(NAME + '-' + str(int(percentage / 10) * 10))
		if self.preferences['display_cpu_average']:
			self.menu_items['cpu'].set_label(
				self.LABEL_CPU.format(percentage)
			)

	def update_cpu_cores(self, percentages):
		if self.preferences['display_cpu_cores']:
			for x in range(len(percentages) / 2):
				self.menu_items['cores'][x].set_label(
					self.LABEL_CORES.format(x*2+1, percentages[x*2], x*2+2, percentages[x*2+1])
				)
			if(len(percentages) % 2 == 1):
				self.menu_items['cores'][len(percentages)/2].set_label(
					self.LABEL_CORE.format(len(percentages), percentages[-1])
				)

	def update_memswap(self, mem_used, mem_total, swap_used, swap_total):
		if self.preferences['display_memory']:
			self.menu_items['memory'].set_label(
				self.LABEL_MEMORY.format(_h(mem_used), _h(mem_total))
			)
		if self.preferences['display_swap']:
			self.menu_items['swap'].set_label(
				self.LABEL_SWAP.format(_h(swap_used), _h(swap_total))
			)


	def update_disk(self, disks):
		if self.preferences['display_disk']:
			for key in disks:
				self.menu_items['disks'][key].set_label(
					self.LABEL_DISK.format(self.preferences['disks'][key],
						_h(disks[key]['used']), _h(disks[key]['total'])
					)
				)

	def update_network(self, receiving, sending, received, sent):
		if self.preferences['display_network_speed']:
			self.menu_items['receiving'].set_label(
				self.LABEL_RECEIVING.format(_h(receiving))
			)
			self.menu_items['sending'].set_label(
				self.LABEL_SENDING.format(_h(sending))
			)

		if self.preferences['display_network_total']:
			self.menu_items['received'].set_label(
				self.LABEL_RECEIVED.format(_h(received))
			)
			self.menu_items['sent'].set_label(
				self.LABEL_SENT.format(_h(sent))
			)

	def system_monitor(self, widget):
		sysmonitors = ['gnome-system-monitor', 'ksysguard', 'htop']
		desktop = os.environ['XDG_CURRENT_DESKTOP']

		if desktop == 'KDE' or len(desktop) == 0:
			sysmonitors.remove('ksysguard')
			sysmonitors.insert(0, 'ksysguard')

		for sysmonitor in sysmonitors:
			try:
				GLib.spawn_async([sysmonitor], flags=GLib.SpawnFlags.SEARCH_PATH)
				break
			except:
				traceback.print_exc()

	def preferences_dialog(self, widget):
		preferences_dialog = PreferencesDialog(self)
		preferences_dialog.update_widgets()
		preferences_dialog.show()

	def apply_preferences(self):
		self.build_menu()
		self.start_suppliers()

	def about(self, widget):
		self.aboutdialog = gtk.AboutDialog()
		self.aboutdialog.set_program_name(DISPLAY_NAME)
		self.aboutdialog.set_version(VERSION)
		self.aboutdialog.set_comments(COMMENTS)
		self.aboutdialog.set_copyright(COPYRIGHT)
		self.aboutdialog.set_website(WEBSITE)
		self.aboutdialog.set_authors(AUTHORS)
		self.aboutdialog.set_license(LICENSE_TEXT)
		self.aboutdialog.set_logo_icon_name(NAME)

		self.aboutdialog.connect('response', self.about_quit)
		self.aboutdialog.show()

	def about_quit(self, widget, event):
		self.aboutdialog.destroy()

	def quit(self, widget):
		gtk.main_quit()

class PreferencesDialog:
	WIDGET_METHODS = {
		'display_': '_active',
		'update_interval_': '_value',
	}

	def __init__(self, indicator):
		self.indicator = indicator
		self.builder = gtk.Builder()
		self.builder.add_from_file(pkg_resources.resource_filename('syspeek.ui','PreferencesDialog.ui'))
		self.dialog = self.builder.get_object('preferences_dialog')
		self.disks = self.builder.get_object('liststore_disks')
		self.dialog.set_title(DISPLAY_NAME + ' ' + _('Preferences'))
		self.builder.connect_signals({
			'on_button_ok_clicked': self.ok,
			'on_button_apply_clicked': self.apply,
			'on_button_cancel_clicked': self.cancel,
		})

	def show(self):
		self.dialog.show()

	def ok(self, widget):
		self.dialog.destroy()
		self.update_preferences()
		self.indicator.preferences.save()
		gobject.idle_add(self.indicator.apply_preferences)

	def apply(self, widget):
		self.update_preferences()
		self.indicator.preferences.save()
		gobject.idle_add(self.indicator.apply_preferences)

	def cancel(self, widget):
		self.dialog.destroy()

	def update_widgets(self):
		for preferences_key in self.indicator.preferences.keys():
			self.update_widget(preferences_key)

		self.update_disks_list()

	def update_disks_list(self):
		for path, name in self.indicator.preferences['disks'].items():
			self.disks.append([name, path])

		treeview_disks = self.builder.get_object('treeview_disks')
		renderer = Gtk.CellRendererText()
		renderer.set_property("editable", True)
		renderer.connect("edited", self.on_disk_name_changed)

		column = Gtk.TreeViewColumn(_('Name'), renderer, text=0)
		column.set_clickable(False)
		treeview_disks.append_column(column)

		column = Gtk.TreeViewColumn(_('Path'), Gtk.CellRendererText(), text=1)
		column.set_clickable(False)
		treeview_disks.append_column(column)

		add_button = self.builder.get_object("add_disk")
		add_button.connect("clicked", self.on_add_disk_button_clicked)

		rm_button = self.builder.get_object("rm_disk")
		rm_button.connect("clicked", self.on_rm_disk_button_clicked)

		self.builder.get_object('display_disk').set_active(len(self.disks) != 0)

	def on_disk_name_changed(self, cell, widget_path, new_text):
		iter = self.disks.get_iter(Gtk.TreePath.new_from_string(widget_path))
		self.disks.set_value(iter, 0, new_text)

	def on_add_disk_button_clicked(self, button):
		file_chooser = Gtk.FileChooserDialog(_('Select Partition to Monitor'),
			self.dialog,
			Gtk.FileChooserAction.SELECT_FOLDER
		)

		file_chooser.add_button(_('_Cancel'), Gtk.ResponseType.CANCEL)
		file_chooser.add_button(_('_Select'), Gtk.ResponseType.ACCEPT)
		file_chooser.set_create_folders(False)
		file_chooser.set_local_only(True)

		if file_chooser.run() == Gtk.ResponseType.ACCEPT:
			path = file_chooser.get_filename()
			name = os.path.basename(path)
			self.disks.append([name if len(name) else _('Root'), path])
			self.builder.get_object('display_disk').set_active(len(self.disks) != 0)

		file_chooser.destroy()

	def on_rm_disk_button_clicked(self, button):
		treeview_disks = self.builder.get_object('treeview_disks')
		try:
			(disks, item) = treeview_disks.get_selection().get_selected()
			disks.remove(item)
			self.builder.get_object('display_disk').set_active(len(disks) != 0)
		except:
			pass

	def update_preferences(self):
		for preferences_key in self.indicator.preferences.keys():
			self.update_preference(preferences_key)

		self.indicator.preferences['disks'] = {}
		for name, path in self.disks:
			self.indicator.preferences['disks'][path] = name

	def update_widget(self, preferences_key):
		self._update(preferences_key, self._update_widget)

	def update_preference(self, preferences_key):
		self._update(preferences_key, self._update_preference)

	def _update(self, preferences_key, update_method):
		for widgets_key in self.WIDGET_METHODS:
			if preferences_key.startswith(widgets_key):
				widget = self.builder.get_object(preferences_key)
				update_method(preferences_key, widget, self.WIDGET_METHODS[widgets_key])
				return

	def _update_widget(self, preferences_key, widget, widget_method):
		if widget is not None:
			method = getattr(widget, 'set' + widget_method)
			method(self.indicator.preferences[preferences_key])

	def _update_preference(self, preferences_key, widget, widget_method):
		if widget is not None:
			method = getattr(widget, 'get' + widget_method)
			self.indicator.preferences[preferences_key] = method()


class Preferences(UserDict):
	FILENAME = os.path.join(GLib.get_user_config_dir(), NAME, 'preferences.json')

	DEFAULT_PREFERENCES = {
		'version': 1,
		'update_interval_cpu': 1.0,
		'update_interval_memswap': 2.0,
		'update_interval_disk': 5.0,
		'update_interval_network': 1.0,
		'display_cpu_average': True,
		'display_cpu_cores': False,
		'display_memory': True,
		'display_swap': True,
		'display_network_speed': True,
		'display_network_total': False,
		'display_disk': True,
		'disks': {
			GLib.get_home_dir(): _('Disk'),
		},
	}

	def save(self):
		if not os.path.exists(os.path.dirname(self.FILENAME)):
			os.makedirs(os.path.dirname(self.FILENAME))

		f = open(self.FILENAME, 'w')
		f.write(json.dumps(self.data, indent=4))
		f.flush()
		f.close()

	def load(self):
		if not os.path.exists(self.FILENAME):
			self.data = self.DEFAULT_PREFERENCES
			self.save()

			old_filename = os.path.join(GLib.get_user_config_dir(), '.' + NAME, os.path.basename(self.FILENAME))
			if os.path.exists(old_filename):
				os.rename(old_filename, self.FILENAME)
				os.removedirs(os.path.dirname(old_filename))
				self.load()

			return

		try:
			f = open(self.FILENAME, 'r')
			self.data = json.loads(f.read())
			f.close()
		except:
			print("ERROR: Could not read preferences file. Loading default values.")
			self.data = self.DEFAULT_PREFERENCES
			self.save()
			return

		self.check()

	def check(self):
		update = False

		for key in self.DEFAULT_PREFERENCES:
			if key not in self.data:
				update = True
				self.data[key] = self.DEFAULT_PREFERENCES[key]

		if self.data['version'] < self.DEFAULT_PREFERENCES['version']:
			# maybe there is the need to do more here in the future
			update = True
			self.data['version'] = self.DEFAULT_PREFERENCES['version']

		for key in self.data:
			if (key in self.DEFAULT_PREFERENCES
				 and ((type(self.data[key]) is not type(self.DEFAULT_PREFERENCES[key])) or
					(key.startswith('update_interval_') and self.data[key] <= 0.0))):
				update = True
				print("ERROR: Invalid value %s for key %s. Setting to default value %s" % \
					(self.data[key], key, self.DEFAULT_PREFERENCES[key]))
				self.data[key] = self.DEFAULT_PREFERENCES[key]

		if update:
			self.save()

