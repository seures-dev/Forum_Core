import os


class ForumAPI:
	api_url: str = ""

	# @classmethod
	# def set_api_url(cls):
	# 	if existing_value := os.environ.get("API_URL"):
	# 		cls.api_url = existing_value
	# 	else:
	# 		raise ValueError

	@staticmethod
	def get_main():
		if existing_value := os.environ.get("API_URL"):
			return existing_value
		else:
			raise ValueError

	@staticmethod
	def get_smoke():
		if existing_value := os.environ.get("API_URL"):
			smoke_url = existing_value + "/smoke"
			return smoke_url
		else:
			raise ValueError

	@staticmethod
	def get_register_url():
		if existing_value := os.environ.get("API_URL"):
			threads_url = existing_value + "/register"
			return threads_url
		else:
			raise ValueError

	@staticmethod
	def get_threads_url():

		if existing_value := os.environ.get("API_URL"):
			threads_url = existing_value + "/threads"
			return threads_url
		else:
			raise ValueError