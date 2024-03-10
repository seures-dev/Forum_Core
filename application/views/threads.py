import math
import threading
import time

import requests
from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from api.forum_api import ForumAPI
from application.models.redis_service import RedisSerializer
from ..models.thread import Thread as ThreadModel
from ..models.branch import Branch as BranchModel
from ..models.post import Post as PostModel


from ..forms import forum_forms
from ..views import get_creators


class Threads:

    @staticmethod
    def get_threads():

        all_thr = ThreadModel.count_threads()

        args = request.args
        try:
            offset = int(args.get("offset", 0))
        except ValueError:
            offset = 0
        offset = offset // 30 * 30
        s = time.time()
        threads = RedisSerializer.Thread.gthreads(offset)

        if not threads:
            print(f"{time.time() - s:.5f} seconds")
            threads = ThreadModel.get_threads_with_offset(offset)
            RedisSerializer.Thread.sthreads(threads, offset)
        if not threads:
            return render_template(
                "forum/threads.html",
            ), 200
        print(f"{time.time() - s:.5f} seconds")

        users_dict = get_creators(threads)

        page_count = (math.ceil(all_thr / 30))
        return render_template(
            "forum/threads.html",
            threads=threads,
            users=users_dict,
            page_count=page_count
        ), 200

    @staticmethod
    def get_thread_by_id(thread_id):
        offset = request.args.get("offset", 0) // 30 * 30
        thread = ThreadModel.get_thread_by_id(thread_id)
        branches = BranchModel.get_branches_by_thread_id(thread_id, offset)
        if not thread:
            abort(404)
        if not branches:
            return render_template(
                "forum/branches_in_thread.html",
                thread=thread,
                branches=[],
                page_count=0
            ), 200
        page_count = math.ceil(thread["branch_count"]/30)
        users_dict = get_creators(branches)
        return render_template(
            "forum/branches_in_thread.html",
            thread=thread,
            branches=branches,
            users=users_dict,
            page_count=page_count
        ), 200

    @staticmethod
    @login_required
    def delete_thread(thread_id):
        def shadow_delete(thread_id):
            branches = BranchModel.delete_all_in_thread(thread_id)
            if branches:
                PostModel.delete_in_branches(branches)
        if current_user.access_level < 1:
            flash("Not enough right.", "negative")
            return redirect(url_for("threads.get_threads"))

        thread = ThreadModel.delete_by_thread_id(thread_id)
        if not thread:
            flash("Thread (already) not exist.", "negative")
            return redirect(url_for("thread.get_threads"))

        shadow_delete_thread = threading.Thread(target=shadow_delete, args=(thread_id,))
        shadow_delete_thread.start()

        flash("Thread delete", "positive")
        return redirect(url_for("thread.get_threads"))


    @staticmethod
    @login_required
    def patch_thread():

        form = forum_forms.ThreadForm()
        args = request.args
        if form.validate_on_submit():
            return {"Message": "ok"}, 200

    @staticmethod
    @login_required
    def create_thread():
        form = forum_forms.ThreadForm()
        if form.validate_on_submit():

            author = {str(current_user.int_id): str(current_user.user_id)}
            thread_id = ThreadModel.get_next_thread_id()
            nthrad = ThreadModel(
                name=form.name.data,
                description=form.description.data,
                creator=author,
                thread_id=thread_id
            )
            nthrad.save()
            send_thread = threading.Thread(target=Threads.send_new_thread, args=(nthrad,current_user.user_id,))
            send_thread.start()
            return redirect(url_for('thread.get_thread_by_id', thread_id=thread_id))
        return render_template("forum/forms/thread_form.html", form=form), 200


    @staticmethod
    def send_new_thread(thread: ThreadModel, user_id):
        url = ForumAPI.get_threads_url()
        data = {
            "thread_name": thread.name,
            "user_id": user_id
        }
        try:
            response = requests.post(url, json=data)
        except requests.exceptions.RequestException as e:
            print(str(e))
            return

        if response.status_code > 201:  # TODO do logging
            print("error")
            print(response.json())
        else:
            print("successful")


    @staticmethod
    def test():
        # form = forum_forms.Reset()
        # return render_template("test.html", form=form)
        pass
