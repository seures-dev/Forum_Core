from flask import Blueprint


thread_router = Blueprint('thread', __name__)


from ..views.threads import Threads

thread_router.route("/", methods=["GET", "POST"])(Threads.get_threads)
thread_router.route("/threads", methods=["GET", "POST"])(Threads.get_threads)
thread_router.route("/threads/create", methods=["GET", "POST"])(Threads.create_thread)


thread_router.route("/<int:thread_id>", methods=["GET", "PATCH", "DELETE"])(Threads.get_thread_by_id)
thread_router.route("/threads/<int:thread_id>", methods=["GET", "PATCH", "POST"])(Threads.get_thread_by_id)
thread_router.route("/threads/<int:thread_id>/delete", methods=["GET", "PATCH", "POST"])(Threads.delete_thread)


thread_router.route("/threads/delete/<int:thread_id>", methods=["GET", "PATCH", "POST"])(Threads.delete_thread)



thread_router.route("/test", methods=["GET", "POST"])(Threads.test)


