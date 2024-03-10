import pathlib
import os
BASE_DIR = pathlib.Path(__file__).parent


class Config:

	MONGO_URI = "mongodb://localhost:27017/data"
	MONGODB_SETTINGS = {
		'db': 'data',
		'port': 27017,
		'host': 'localhost',
	}
	URL_KEY = "MY_URL_KEY"
	REDIS_URL = "redis://localhost:6379/0"
	SECRET_KEY = "Some_secret_key"


	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SQLALCHEMY_ECHO = False

	@staticmethod
	def token_key():
		if existing_value := os.environ.get("TOKEN_KEY"):
			return existing_value
		else:
			raise ValueError("NOT TOKEN_KEY")

	@staticmethod
	def get_mail():
		if existing_value := os.environ.get("GMAIL_MAIL"):
			return existing_value
		else:
			raise ValueError("NOT GMAIL_MAIL")

	@staticmethod
	def get_mail_password():
		if existing_value := os.environ.get("GMAIL_PASSWORD"):
			return existing_value
		else:
			raise ValueError("NOT GMAIL_PASSWORD")


	@staticmethod
	def get_host_port():
		if existing_value := os.environ.get("HOST_PORT"):
			return existing_value
		else:
			raise ValueError("NOT HOST_PORT")





