from flask import Blueprint


control_blueprint = Blueprint('control', __name__)


from ..views.control import Control

control_blueprint.route("/drop_hashes/<key>", methods=["GET", "POST"])(Control.drop_hash)
control_blueprint.route("/control/upload_all", methods=["GET"])(Control.upload_all)
control_blueprint.route("/control/posts", methods=["GET"])(Control.upl_posts)
control_blueprint.route("/control/branches", methods=["GET"])(Control.upl_branches)
control_blueprint.route("/control/threads", methods=["GET"])(Control.upl_threads)
