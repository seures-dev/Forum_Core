
from application.models.redis_service import RedisSerializer
from ..models.user import User as UserModel



def some_func():
    print("some_func")


def get_creators(items,):
    users = set()
    for itm in items:
        users.add(*itm['creator'].values())

    objects_list = UserModel.objects(user_id__in=users)
    users_dict = {}
    for user in objects_list:
        RedisSerializer.User.suser(user, True)
        users_dict[user.int_id] = user.nickname

    return users_dict