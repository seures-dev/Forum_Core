import math
from datetime import datetime
import time
import requests

from api.forum_api import ForumAPI
from application import mongo_db, redis_store
from ..models.thread import Thread as ThreadModel
from ..models.user import User as UserModel
from ..models.branch import Branch as BranchModel
from ..models.post import Post as PostModel
import threading


class Control:

    @staticmethod
    def drop_hash(key=None):
        if key == "fkojnsdihf9u8sd7f8sdf":
            print("redis hashes dropped")
            redis_store.flushall()
            return {"msg": "dropped"}, 200
        return {"msg": "wtf"}, 400

    @classmethod
    def upl_threads(cls):
        response = requests.get(ForumAPI.get_threads_url() + "?getall=1")
        threads = response.json()
        thrs = set()
        ThreadModel.objects.delete({})
        for thread in threads:
            creator_id = thread["creator_id"]
            author = UserModel.objects(_int_id=creator_id).first()

            if not author:
                creator = None
            else:
                creator = {str(creator_id): author.get_id()}
            tid = thread["thread_id"]
            if tid not in thrs:
                thrs.add(tid)
            else:
                raise ValueError(f"Thread already exist: {tid}")
            nthread = ThreadModel(
                name=thread["name"],
                thread_id=thread["thread_id"],
                description=thread.get("description"),
                creator=creator,
                created=datetime.strptime(thread["created_date"], "%Y-%m-%d-%H:%M:%S"),
                branch_count=thread["branch_count"],
                pinned_thread=False
            )
            nthread.save()

        return threads, 200

    @classmethod
    def upl_branches(cls):
        response = requests.get("http://127.0.0.1:5000/branches?getall=1")
        data = response.json()
        BranchModel.objects.delete({})

        for branch in data:
            creator_id = branch["creator_id"]
            author = UserModel.objects(_int_id=creator_id).first()
            creator = {str(creator_id): author.get_id()}

            nbranch = BranchModel(
                name=branch["branch_name"],
                description=branch["branch_name"] + ' created by ' + author.nickname,
                branch_id=branch["branch_id"],
                thread_id=branch["thread_id"],
                creator=creator,
                created=datetime.strptime(branch["created_date"], "%Y-%m-%d-%H:%M:%S"),
                posts_count=branch["message_count"]
            )
            nbranch.save()

        return {"msg": "some posts"}, 200

    @classmethod
    def upl_posts(cls):
        info_request = requests.get("http://127.0.0.1:5000/posts/1/2?get_count=1")
        resp = info_request.json()
        chunk_size = resp["chunk_size"]
        post_count = resp["post_count"]
        print(f"post count: {post_count}, chunk size: {chunk_size}")
        requests_count = math.ceil(post_count / chunk_size)
        thr = []
        last = 0
        for i in range(10, 151, 10):
            nthre = threading.Thread(target=cls.threading_post_upl, args=(last, i))
            thr.append(nthre)
            nthre.start()
            last = i+1
            print("i:", i)
        return {
            "chunk_size": chunk_size,
            "post_count": post_count,
            "requests_count": requests_count,
        }, 200


    @classmethod
    def threading_post_upl(cls, from_n, to_n):

        print(f"Thread: f:{from_n}, tp:{to_n}")
        chunk_num = from_n
        post_count = 0
        response = requests.get(f"http://127.0.0.1:5000/posts/1/2?getall={chunk_num}")
        user_dcit = {}
        while response.json() and chunk_num <= to_n:
            posts = response.json()
            post_count += len(posts)
            posts_docs = []
            for post in posts:
                creator_id = post["creator_id"]
                if not creator_id in user_dcit.keys():
                    author = UserModel.objects(_int_id=creator_id).first()
                    creator = {str(creator_id): author.get_id()}
                    user_dcit[creator_id] = creator
                else:
                    creator = user_dcit.get(creator_id)
                posts_docs.append(PostModel(
                    u_id=post["u_id"],
                    branch_id=post["branch_id"],
                    into_branch_id=post["into_branch_id"],
                    creator=creator,
                    created=datetime.strptime(post["created_date"], "%Y-%m-%d-%H:%M:%S"),
                    content=post["content"],
                ))

                time.sleep(0.0001)
            PostModel.objects.insert(posts_docs)
            print(f"posts in chunk[{chunk_num}]:", len(posts), "post saved")
            chunk_num += 1
            time.sleep(0.01)
            response = requests.get(f"http://127.0.0.1:5000/posts/1/2?getall={chunk_num}")
        print(f"{'='*5} Thread: f:{from_n}, tp:{to_n} posts: {post_count} {'='*5}")


    @classmethod
    def upload_all(cls):
        cls.upl_threads()
        cls.upl_branches()
        # cls.upl_posts()
        return {"msg": "success"}, 200
