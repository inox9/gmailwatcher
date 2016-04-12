import imaplib
import socket
import time
import re

class ImapGmailClient:
	IMAP_HOST = 'imap.gmail.com'

	def __init__(self, login, password):
		socket.setdefaulttimeout(10)
		self.imap = None
		self.username = login
		self.password = password
		self.authorized = False
		self._connect()

	def __del__(self):
		if self.authorized:
			self.imap.logout()

	def _connect(self):
		self.imap = imaplib.IMAP4_SSL(self.IMAP_HOST)

	def _reconnect(self):
		tries = 0
		self.authorized = False
		while tries < 3:
			try:
				self._connect()
				self.login()
			except Exception:
				tries += 1
				time.sleep(5)

	def login(self):
		try:
			self.imap.login(self.username, self.password)
		except imaplib.IMAP4.error as e:
			self.authorized = False
			if 'AUTHENTICATIONFAILED' in e.message:
				raise AuthErrorException('Wrong credentials for %s'.format(self.login))
			else:
				raise
		self.authorized = True

	def logout(self):
		if not self.authorized:
			raise NotAuthorizedException('You should be authorized to perform logout')
		self.imap.logout()
		self.authorized = False

	def get_new_mail_count(self):
		if not self.authorized:
			self._reconnect()
			if not self.authorized:
				return False
		try:
			x, y = self.imap.status('INBOX','(MESSAGES UNSEEN)')
		except Exception:
			self.authorized = False
			return False
		return int(re.search(r'UNSEEN\s+(\d+)', y[0]).group(1))

class AuthErrorException(Exception):
	pass

class NotAuthorizedException(Exception):
	pass