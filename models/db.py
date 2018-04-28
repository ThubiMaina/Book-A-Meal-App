from flask import Flask
from flask_bcrypt import Bcrypt

class User:
	def __init__(self, username, email, password, user_id):
		self.username = username
		self.email = email
		self.password = Bcrypt().generate_password_hash(password).decode()
		self.user_id = user_id
