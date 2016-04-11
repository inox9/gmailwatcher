#!/usr/bin/env python

# found on <http://files.majorsilence.com/rubbish/pygtk-book/pygtk-notebook-html/pygtk-notebook-latest.html#SECTION00430000000000000000>
# simple example of a tray icon application using PyGTK

import threading
import gobject
import gtk
import watcherthread
import config
import sys
import json
import os
import subprocess as sp

gobject.threads_init()

def message(data=None):
	msg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, data)
	msg.run()
	msg.destroy()

def close_app(data=None):
	gtk.main_quit()

def update_now(data=None):
	upd_event.set()
	upd_event.clear()

def make_menu(event_button, event_time, data=None):
	menu = gtk.Menu()
	exit_item = gtk.ImageMenuItem(gtk.STOCK_QUIT)
	exit_item.set_label('Quit')
	update_item = gtk.ImageMenuItem(gtk.STOCK_REFRESH)
	update_item.get_children()[0].set_markup('<b>Check now</b>')
	menu.append(update_item)
	menu.append(gtk.SeparatorMenuItem())
	menu.append(exit_item)
	update_item.connect_object("activate", update_now, "Check now")
	exit_item.connect_object("activate", close_app, "Exit")
	menu.show_all()
	menu.popup(None, None, None, event_button, event_time)

def on_right_click(data, event_button, event_time):
	make_menu(event_button, event_time)

def get_config_json():
	if not os.path.exists(config.ENCRYPTED_CONFIG_PATH):
		message("{0} does not exist, you should create your config.json from _config.json and encrypt it with GPG first".format(config.ENCRYPTED_CONFIG_PATH))
		sys.exit(4)
	try:
		cmd = ['gpg', '-o-']
		params = []
		if '-' in sys.argv:
			params = [sys.stdin.read().strip()]
			cmd += ['--passphrase-fd', '0']
		cmd.append(config.ENCRYPTED_CONFIG_PATH)
		p = sp.Popen(cmd, stdout=sp.PIPE, stdin=sp.PIPE, stderr=sp.PIPE)
		out = p.communicate(*params)[0]
	except sp.CalledProcessError:
		message('Wrong decrypt password supplied, exiting!')
		sys.exit(1)
	try:
		js = json.loads(out)
	except ValueError:
		message('Cannot decode JSON, exiting!')
		sys.exit(2)
	for el in js:
		if len(el) != 2:
			message('JSON structure is not valid, valid is [["login1", "password1"], ["login2", "password2"], ...]')
			sys.exit(3)
	return js

if __name__ == '__main__':
	conf = get_config_json()
	icon = gtk.status_icon_new_from_file(config.ICON_INACTIVE)
	icon.connect('popup-menu', on_right_click)
	upd_event = threading.Event()
	wt = watcherthread.WatcherThread(conf, icon, upd_event)
	wt.daemon = True
	icon.set_tooltip_markup('<b>{0}</b>'.format(wt.APP_NAME))
	wt.start()
	gtk.main()
