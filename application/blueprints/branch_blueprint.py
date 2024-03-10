from flask import Blueprint


branch_router = Blueprint("branch_router", __name__, url_prefix="/threads/<int:thread_id>")


from ..views.branches import Branches


branch_router.route("/branches/<int:branch_id>", methods=["GET", "PATCH", "DELETE"])(Branches.get_branch_by_id)
branch_router.route("/branches/create", methods=["GET", "POST"])(Branches.create_branch)
branch_router.route("/branches/<int:branch_id>/create-post", methods=["GET", "POST"])(Branches.create_post)
branch_router.route("/branches/admin/<key>", methods=["GET"])(Branches.recalculate_posts)





