from threading import Thread
import imapgmailclient
import gobject
import config

class WatcherThread(Thread):
	APP_NAME = 'GMailWatcher 0.1'

	def __init__(self, credentials, icon, upd_event):
		super(WatcherThread, self).__init__()
		self.credentials = credentials # [(login1,password1), (login2,password2)]
		self.error_count = 0
		self.tray_icon = icon
		self.upd_event = upd_event

	def run(self):
		while True:
			all_nm_count = 0
			tooltip = []
			for creds in self.credentials:
				igc = imapgmailclient.ImapGmailClient(*creds)
				try:
					igc.login()
				except imapgmailclient.AuthErrorException:
					self.error_count += 1
					tooltip.append('Auth error for {0}'.format(creds[0]))
					continue
				except Exception as e:
					self.error_count += 1
					print e
					continue
				count = igc.get_new_mail_count()
				if count is False:
					tooltip.append('Fetching new mail error in {0}'.format(creds[0]))
				else:
					all_nm_count += count
					if count > 0:
						tooltip.append('{0} new in {1}'.format(count, creds[0]))
				del igc
			gobject.idle_add(self.set_icon_state, all_nm_count)
			gobject.idle_add(self.set_icon_tooltip, tooltip)
			self.upd_event.wait(float(config.CHECK_INTERVAL))

	def set_icon_state(self, count):
		self.tray_icon.set_from_file(config.ICON_ACTIVE if count > 0 else config.ICON_INACTIVE)

	def set_icon_tooltip(self, tooltip):
		if not tooltip:
			tooltip.append('No new mail')
		tooltip.insert(0, '<b>{0}</b>'.format(self.APP_NAME))
		self.tray_icon.set_tooltip_markup('\n'.join(tooltip))
