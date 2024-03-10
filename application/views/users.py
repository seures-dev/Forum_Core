
import uuid
import requests
import threading
from datetime import datetime, date, timedelta
from itsdangerous import URLSafeSerializer, BadSignature, SignatureExpired, BadData

from api.forum_api import ForumAPI
from config import Config
from ..tools.email_sender import send_email

from ..forms import user_forms
from ..models.user import User as UserModel
from application.models.redis_service import RedisSerializer

from validate_email import validate_email

from flask import render_template, redirect, request, url_for, abort, flash
from flask_login import login_user, logout_user, login_required


class User:

	@staticmethod
	def user_url(user=None):
		if not user:
			return redirect(url_for("user_router.signin"))
		user = UserModel.objects(nickname=user).first()
		return {"msg": f"welcome {user.nickname}", "confirm": user.confirmation}, 200

	@staticmethod
	def signup():

		form = user_forms.SignUp()
		print(request.remote_addr)
		print(request.remote_user)
		if form.validate_on_submit():

			user_uuid = str(uuid.uuid4())
			user = UserModel(
				user_id=user_uuid,
				nickname=form.nickname.data,
				phone=form.phone.data,
				email=form.email.data,
				confirmation=False,
				password=form.password.data,
				create_time=date.today()
			)
			user_data = {
				"user_id": user_uuid,
				"exp": (datetime.utcnow() + timedelta(days=30)).timestamp()
			}

			serializer = URLSafeSerializer(Config.URL_KEY)
			url_token = serializer.dumps(user_data)
			new_user = {
				"name": user.nickname,
				"email": user.email,
				"password": user.password
			}
			user.save()

			confirm_url = url_for("user_router.confirm", token=url_token, _external=True)
			html_doc = render_template(
				"mail/mail_template.html",
				confirm_url=confirm_url,
				msg="Please click on the following link to confirm your email address."
			)
			#print(confirm_url, user.nickname)
			send_email(user.email, "Confirm your email", html_doc)
			flash("Check your emails to confirm your email address.", "positive")
			send_user_thread = threading.Thread(target=User.send_new_user, args=[new_user, user,])
			send_user_thread.start()
			return redirect(url_for("user_router.signin"))

		return render_template("user/signup.html", form=form, title="Sign up")

	@staticmethod
	def send_new_user(user_data, user):
		try:
			response = requests.post(ForumAPI.get_register_url(), json=user_data)
		except requests.exceptions.ConnectionError:
			print("no connection")
			return
		if response:
			user_resp = response.json()
			user_id = user_resp["user_id"]
			user.user_id = user_id
			user.save()
			print("create new user ")
		else:
			print("no data")

	@staticmethod
	def confirm(token):
		serializer = URLSafeSerializer(Config.URL_KEY)
		try:
			data = serializer.loads(token)
			user_uuid = data["user_id"]
		except (KeyError, BadSignature, BadData):
			return abort(404)
		except SignatureExpired:
			return abort(404)
		user: UserModel = UserModel.objects(user_id=user_uuid).first()
		if not user:

			return abort(404)
		if user.confirmation:
			flash('Account already confirmed.', 'positive')

			us = RedisSerializer.User.guser(user_uuid)
			#print(us)
			return redirect(url_for("user_router.signin"), code=200)  # TODO add flash "confirm" and "already confirm"
		user.confirmation = True
		user.save()
		RedisSerializer.User.suser(user)
		flash('Account confirmed.', 'positive')
		return redirect(url_for("user_router.signin"), code=200)  # TODO add flash "confirm" and "already confirm"

	@staticmethod
	def signin():
		form = user_forms.Login()
		if form.validate_on_submit():
			login = form.email.data
			if validate_email(login):
				user = UserModel.objects(mail=login).first()
			else:
				user = UserModel.objects(nickname=login).first()

			if not user:
				flash("You entered incorrect user data.", "negative")
				return redirect(url_for("user_router.signin"))
			RedisSerializer.User.suser(user)
			if form.password.data != user.password:
				flash("You entered incorrect user data.", "negative")
				return redirect(url_for("user_router.signin"))
			if not user.confirmation:
				flash("Confirm your account.", "negative")
				return redirect(url_for("user_router.signin"))
			login_user(user)
			flash('Successfully signed in.', 'positive')
			next_page = request.args.get("next")
			print(next_page)
			if next_page:
				return redirect(next_page)
			return redirect(url_for('user_router.account'))
		next_page = request.args.get("next")
		return render_template("user/signin.html",  form=form, title="Sign in", next_page=next_page), 200

	@staticmethod
	@login_required
	def account():

		return render_template("user/account.html", avatar="img/img.png")

	@staticmethod
	def logout():
		logout_user()
		return redirect(url_for("user_router.signin"))

	@staticmethod
	def forgot():

		form = user_forms.Forgot()

		if form.validate_on_submit():

			user = UserModel.objects(email=form.email.data).first()
			if not user:
				abort(404)

			user_data = {
				"user_id": user.user_id,
				"mail": user.email,
				"exp": (datetime.utcnow() + timedelta(minutes=30)).timestamp()
			}
			serializer = URLSafeSerializer(Config.URL_KEY)
			url_token = serializer.dumps(user_data)
			confirm_url = url_for("user_router.reset", token=url_token, _external=True)
			msg = ("If you receive this message, it means they are trying to change your password, "
				   "if it’s you, follow the link, but if it’s not you, do nothing")
			html_doc = render_template(
				"mail/mail_template.html",
				confirm_url=confirm_url,
				msg=msg
			)
			send_email(user.email, "Reset your password", html_doc)
			RedisSerializer.set_value(f"TMP-forgot:{form.email.data}", 1)

			flash("Check your email to reset password", "success")

			return redirect(url_for("user_router.signin"))

		return render_template(
			"user/forgot.html",
			form=form
		)


	@staticmethod
	def reset(token):
		serializer = URLSafeSerializer(Config.URL_KEY)

		try:
			data = serializer.loads(token)
			user_uuid = data["user_id"]
			email = data["mail"]

		except (KeyError, BadSignature, BadData):
			return abort(404)

		except SignatureExpired:
			return abort(404)

		if tmp := RedisSerializer.get_value(f"TMP-forgot:{email}"):
			try:
				tmp = int(tmp)
				if tmp > 1:
					abort(404)

			except ValueError:
				return abort(404)

		form = user_forms.Reset()

		if form.validate_on_submit():

			user: UserModel = UserModel.objects(user_id=user_uuid).first()
			if not user:
				return abort(404)

			user.password = form.password.data
			user.save()
			flash('Password changed, sign in please', 'positive')
			RedisSerializer.set_value(f"TMP-forgot:{email}", 10)
			return redirect(url_for("user_router.signin"))

		return render_template("user/reset.html", form=form, token=token)

	@staticmethod
	def user_by_id(user_id):
		user = RedisSerializer.User.guser(user_id, True)
		if not user:
			user = UserModel.objects(_int_id=user_id).first()
		return {"user_id": user.nickname}, 200

	@staticmethod
	def upload_all_user_from_api():
		resp = requests.get("http://127.0.0.1:5000/users/1?get_all=1")
		data = resp.json()
		users = []
		for user in data:
			us = UserModel(
				nickname=user["name"],
				email=user['email'],
				password=user['password_hash'],
				_int_id=user['user_id'],
				create_time=datetime.strptime(user["created"], "%Y-%m-%d-%H:%M:%S"),
				confirmation=True,
				access_level=user['access_level'],
				user_id=str(uuid.uuid4())
			)
			us.save()
