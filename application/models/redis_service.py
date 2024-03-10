import copy
import time
import json
from json import JSONDecodeError,JSONEncoder
import pickle

from application import redis_store
from application.models.user import User as UserModel
from redis import ConnectionError, TimeoutError






def no_redis_check(func):
    def wrapped(*args, **kwargs):
        try:
            s = time.time()
            result = func(*args, **kwargs)
            print(f"do {func.__name__} : spend{time.time() - s:.5f}")
        except (ConnectionError, TimeoutError):
            print("No redis connection")
            return None
        except KeyError:
            print("KeyError, JSONEncoder")
            print("Ex:", args, kwargs)
            return None
        except JSONDecodeError:
            print("JSONDecodeError")
            return None
        except TypeError:
            print("TypeError")
            return None
        except Exception as e:  # Перехват любого другого исключения
            print(f"An error occurred: {e}")
            return None
        return result

    return wrapped
    # return staticmethod(wrapped)


class RedisSerializer:

    @staticmethod(no_redis_check)
    def set_value(key, value, ex_min=30):
        """set data to redis by key, value, expire time"""
        redis_store.set(key, value, ex=ex_min*60)

    pass

    @staticmethod(no_redis_check)
    def get_value(key):
        return redis_store.get(key)

    class Thread:

        @staticmethod(no_redis_check)
        def gthreads(offset=0):
            s = time.time()
            if offset % 30 != 0:
                offset = offset // 30 * 30
            threads_keys = redis_store.lrange(f"threads:{offset}", 0, -1)
            print(f"do threads_keys : spend{time.time() - s:.5f}")
            if not threads_keys:
                return None
            redis_data = redis_store.mget(threads_keys)
            thread_data = [json.loads(x) for x in redis_data]
            for thr in thread_data:
                moderators = thr.pop("moderators")
                creator: dict = thr.pop("creator")
                thr["creator"] = {int(next(iter(creator))): list(creator.values())[0]}
                thr["moderators"] = {int(key): value for key, value in moderators.items()}

            return thread_data
        @staticmethod(no_redis_check)
        def sthreads(threads, offset=0):
            if offset % 30 != 0:
                offset = offset // 30 * 30

            thread_dicts = {}
            keys_list = []
            threads_list_key = f"threads:{offset}"

            for itm in threads:
                thread_id = itm["thread_id"]
                keys_list.append(f"thread:{thread_id}")
                thread_dicts[f"thread:{thread_id}"] = itm

            if redis_store.llen(threads_list_key) > 0:
                redis_store.delete(threads_list_key)
            for key, value in thread_dicts.items():
                redis_store.expire(key, 1800)
                redis_store.rpush(threads_list_key, key)

            redis_store.expire(threads_list_key, 1800)

        @staticmethod(no_redis_check)
        def sthread_by_id(thread_id, thread, branches=None, offsest=0):
            print(thread)
            key = f"thread:{thread_id}"
            thread = copy.copy(thread)
            if "branches" in thread.keys():
                b = RedisSerializer.Branch.sbranches(thread["branches"], offsest)
                thread["branches"] = b
            elif branches:
                b = RedisSerializer.Branch.sbranches(branches)
                thread["branches"] = b
            redis_store.hset(key, mapping=thread)
            redis_store.expire(key, 1800)

        @staticmethod(no_redis_check)
        def gthread_by_id(thread_id):
            thread = redis_store.hgetall(f"thread:{thread_id}")
            # print(thread)
            if not thread:
                return
            thread_dict = {key.decode(): value.decode() for key, value in thread.items()}
            if thread_dict.get("branches"):
                thread_dict["branches"] = RedisSerializer.Branch.gbranches(branch_str=thread_dict["branches"])
            # print(thread_dict)
            return thread_dict

        @staticmethod(no_redis_check)
        def gthreads_by_creator():
            pass

    class Branch:
        @staticmethod(no_redis_check)
        def sbranches(branches, offset=0):
            branches_list = []
            for val in branches:
                print(val)
                key = f"branch:{val['branch_id']}"
                redis_store.hset(key, mapping=val)
                redis_store.expire(key, 1800)
                branches_list.append(key)

            return ','.join(branches_list)

        @staticmethod(no_redis_check)
        def gbranches(offset=0, branch_str=None):
            if branch_str:
                branch_list = []
                branches_keys = branch_str.split(",")
                for branch in branches_keys:
                    value = {key.decode(): value.decode() for key, value in redis_store.hgetall(branch).items()}
                    branch_list.append(value)
                return branch_list

        @staticmethod(no_redis_check)
        def gbranch_by_id(branch_id):
            key = f"branch:{branch_id}"
            redis_data = redis_store.get(key)
            if not redis_data:
                return
            data = json.loads(redis_data)
            return data

        @staticmethod(no_redis_check)
        def sbranch(branch):

            key = f"branch:{branch['branch_id']}"
            data = json.dumps(branch)
            redis_store.set(key, data)


    class Post:
        @staticmethod(no_redis_check)
        def gposts(branch_id, offset):
            key = f"post-{branch_id}:{offset}"
            redis_data = redis_store.get(key)
            if not redis_data:
                return None
            data = json.loads(redis_data)
            return list(data.values())


        @staticmethod(no_redis_check)
        def sposts(branch_id, offset, posts):

            post_dict = {post["into_branch_id"]: post for post in posts}
            key = f"post-{branch_id}:{offset}"
            json_data = json.dumps(post_dict)
            redis_store.set(key, json_data)

    class User:

        @staticmethod(no_redis_check)
        def suser(user: UserModel, by_int_id=False):
            key = f"user:{user.user_id}"
            user_data = pickle.dumps(user)
            if by_int_id:
                redis_store.hset("users", user.int_id, user_data)
                redis_store.expire("users", 1800)
                return
            redis_store.set(key, user_data, ex=60 * 30)

        @staticmethod(no_redis_check)
        def guser(user_id, by_int_id=False) -> UserModel | None:
            if by_int_id:
                user_data = redis_store.hget("users", user_id)
            else:
                key = f"user:{user_id}"
                user_data = redis_store.get(key)
            if not user_data:
                return
            user = pickle.loads(user_data)
            if not isinstance(user, UserModel):
                return

            return user
