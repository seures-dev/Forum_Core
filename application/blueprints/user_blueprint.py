from flask import Blueprint


user_router = Blueprint("user_router", __name__, url_prefix="/user")


from ..views.users import User


#user_router.route("/<user>/info", methods=["GET", "POST"])(User.user_url)
user_router.route("/", methods=["GET", "POST"])(User.user_url)
user_router.route("/<int:user_id>", methods=["GET", "POST"])(User.user_by_id)

user_router.route("/signup", methods=["GET", "POST"])(User.signup)
user_router.route("/signin", methods=["GET", "POST"])(User.signin)
user_router.route("/logout", methods=["GET", "POST"])(User.logout)

user_router.route("/confirm/<token>", methods=["GET", "POST"])(User.confirm)

user_router.route("/account", methods=["GET", "POST"])(User.account)
user_router.route("/forgot", methods=["GET", "POST"])(User.forgot)
user_router.route("/reset/<token>", methods=["GET", "POST"])(User.reset)




