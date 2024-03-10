from flask import Flask
from flask_mongoengine import MongoEngine
from flask_redis import FlaskRedis
from flask_wtf.csrf import CSRFProtect

import config
from application.models.user import User as UserModel


app = Flask(__name__)
app.config.from_object(config.Config)


mongo_db = MongoEngine(app)

redis_store = FlaskRedis(app, socket_timeout=0.1)

csrf = CSRFProtect(app)


from application.blueprints.thread_blueprint import thread_router
from application.blueprints.controll_blueprint import control_blueprint
from application.blueprints.branch_blueprint import branch_router
from application.blueprints.user_blueprint import user_router

app.register_blueprint(thread_router)
app.register_blueprint(control_blueprint)
app.register_blueprint(branch_router)
app.register_blueprint(user_router)


from flask_login import LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "user_router.signin"



@login_manager.user_loader
def load_user(user_id):
    from application.models.redis_service import RedisSerializer
    user = RedisSerializer.User.guser(user_id)
    if user is None:
        user = UserModel.objects(user_id=user_id).first()
        RedisSerializer.User.suser(user)
    if not user.confirmation:
        return None

    return user


