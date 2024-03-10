from mongoengine import Document, StringField, DateTimeField, IntField, DictField
from datetime import datetime
from bson import ObjectId

from ..models.post import Post as PostModel

class Branch(Document):
    branch_id = IntField(primary_key=True)
    name = StringField()
    thread_id = IntField(required=True)
    description = StringField()
    creator = DictField(field=StringField())
    created = DateTimeField(default=datetime.now())
    moderators = DictField(field=StringField())
    moderators_count = IntField()
    posts_count = IntField(default=0)

    @property
    def id(self):
        return self.branch_id

    def to_dict(self):
        obj_dict = {}
        for field in self._fields.keys():
            value = getattr(self, field, None)
            if value is None:
                continue
            if isinstance(value, datetime):
                create_time = str(value)
                obj_dict[field] = create_time
                continue
            if isinstance(value, ObjectId):
                obj_dict[field] = str(value)
                continue
            if value == self.creator and isinstance(value, dict):
                key = next(iter(value.keys()))
                new_value = {int(key): value[key]}
                obj_dict[field] = new_value
                continue

            obj_dict[field] = value
        return obj_dict

    @classmethod
    def get_branches_by_thread_id(cls, thread_id, offset):
        branches = cls.objects.order_by("branch_id").filter(thread_id=thread_id).skip(offset).limit(30).all()
        if branches:
            return [x.to_dict() for x in branches]
        return None

    @classmethod
    def delete_all_in_thread(cls, thread_id):
        branch_ids = tuple(obj.branch_id for obj in cls.objects.filter(thread_id=thread_id))
        cls.objects(thread_id=thread_id).delete()
        return branch_ids

    @classmethod
    def get_branch_by_id(cls, branch_id):
        branch = cls.objects.filter(branch_id=branch_id).first()
        return branch.to_dict() if branch else None

    @classmethod
    def get_next_branch_id(cls):
        branch = cls.objects.order_by("-branch_id").limit(1).first()
        return branch.branch_id + 1

    @classmethod
    def increase_post_count(cls, branch_id):
        cls.objects.filter(branch_id=branch_id).first().post_count += 1
    @classmethod
    def decrease_post_count(cls, branch_id):
        cls.objects.filter(branch_id=branch_id).first().post_count -= 1

    @classmethod
    def _recalculate(cls):
        branches = tuple(cls.objects.all())
        for branch in branches:
            print(branch.posts_count if branch.posts_count else "none", end="  ")
            branch.posts_count = PostModel.count(branch.branch_id)
            print(branch.posts_count)
            branch.save()
