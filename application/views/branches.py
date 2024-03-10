import math

from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user
from application.models.redis_service import RedisSerializer

from ..forms import forum_forms

from ..models.thread import Thread as ThreadModel
from ..models.branch import Branch as BranchModel
from ..models.post import Post as PostModel

from ..views import get_creators


class Branches:
    @staticmethod
    def get_branch_by_id(thread_id, branch_id):

        args = request.args
        try:
            offset = int(args.get("offset", 0))
        except ValueError:
            offset = 0
        offset = offset // 30 * 30
        branch = RedisSerializer.Branch.gbranch_by_id(branch_id)
        if not branch:
            branch = BranchModel.get_branch_by_id(branch_id)
            RedisSerializer.Branch.sbranch(branch)
        posts = RedisSerializer.Post.gposts(branch_id, offset)
        if not posts:
            posts = PostModel.get_posts_by_branch_id(branch_id, offset)
        if not posts:
            return render_template(
                "forum/posts_in_branch.html",
                branch=branch,
                posts=[],
                page_count=0,
            )
        users_dict = get_creators(posts)

        all_posts = PostModel.count(branch_id)
        print(all_posts)
        page_count = (math.ceil(all_posts / 30))

        return render_template(
            "forum/posts_in_branch.html",
            branch=branch,
            posts=posts,
            users=users_dict,
            page_count=page_count,
        )

    @staticmethod
    @login_required
    def create_branch(thread_id):  # TODO добавить удаление бранчей и постов
        form = forum_forms.BranchForm()
        thread = ThreadModel.get_thread_by_id(thread_id)
        if form.validate_on_submit():
            branch_id = BranchModel.get_next_branch_id()
            author = {str(current_user.int_id): str(current_user.user_id)}
            n_branch = BranchModel(
                thread_id=thread_id,
                branch_id=branch_id,
                name=form.name.data,
                description=form.description.data,
                creator=author,
            )
            try:
                n_branch.save()
                ThreadModel.increase_branch_count(thread_id)
            except Exception as e:
                print(str(e))
            return redirect(url_for(
                "branch_router.get_branch_by_id",
                thread_id=thread_id,
                branch_id=branch_id
            ))

        return render_template("forum/forms/branch_form.html", thread=thread, form=form)

    @staticmethod
    @login_required
    def create_post(thread_id, branch_id):
        form = forum_forms.PostForm()
        branch = BranchModel.get_branch_by_id(branch_id)
        author = {str(current_user.int_id): str(current_user.user_id)}
        if form.validate_on_submit():
            post_uid, into_branch_id = PostModel.get_next_id(branch_id)
            print(f"u_id: {post_uid}, into_branch_id: {into_branch_id}")
            new_post = PostModel(
                u_id=post_uid,
                into_branch_id=into_branch_id,
                content=form.content.data,
                branch_id=branch_id,
                creator=author
            )

            try:
                new_post.save()
                BranchModel.increase_post_count(branch_id)
            except Exception as e:
                print(str(e))

            return redirect(url_for(
                "branch_router.get_branch_by_id",
                thread_id=thread_id,
                branch_id=branch_id
            ))
        return render_template(
            "forum/forms/post_form.html",
            branch=branch,
            form=form,
        )

    @staticmethod
    def recalculate_posts(thread_id,key):
        if key == "asdkn21ih812geh87asghduas":
            BranchModel._recalculate()
        return redirect(url_for("thread.get_threads"))