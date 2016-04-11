import imaplib
import socket
import re

class ImapGmailClient:
	def __init__(self, login, password):
		socket.setdefaulttimeout(10)
		self.imap = imaplib.IMAP4_SSL('imap.gmail.com')
		self.username = login
		self.password = password
		self.authorized = False

	def __del__(self):
		if self.authorized:
			self.imap.logout()

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
			raise NotAuthorizedException('You should be authorized to get new mail count')
		x,y = self.imap.status('INBOX','(MESSAGES UNSEEN)')
		return int(re.search(r'UNSEEN\s+(\d+)', y[0]).group(1))

class AuthErrorException(Exception):
	pass

class NotAuthorizedException(Exception):
	pass