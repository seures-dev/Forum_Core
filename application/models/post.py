from mongoengine import Document, StringField, DateTimeField, IntField, DictField
from datetime import datetime
from bson import ObjectId

class Post(Document):
    u_id = IntField(primary_key=True)
    branch_id = IntField(required=True)
    into_branch_id = IntField(required=True)
    creator = DictField(field=StringField())
    created = DateTimeField(default=datetime.now())
    content = StringField()

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
    def get_posts_by_branch_id(cls, branch_id, offset):
        posts = cls.objects.order_by("into_branch_id").filter(branch_id=branch_id).skip(offset).limit(30).all()
        return [x.to_dict() for x in posts] if posts else None

    @classmethod
    def get_post_by_id(cls, post_id):
        post = cls.objects.filter(u_id=post_id).first()
        return post.to_dict() if post else None

    @classmethod
    def count(cls, branch_id):
        return cls.objects.filter(branch_id=branch_id).count()

    @classmethod
    def get_next_id(cls, branch_id):
        last_post_in_branch = cls.objects.filter(branch_id=branch_id).order_by("-into_branch_id").limit(1).first()
        last_post = cls.objects.order_by("-u_id").limit(1).first()
        into_branch_id = last_post_in_branch.into_branch_id if last_post_in_branch else 0
        u_id = last_post.u_id if last_post else 0

        return u_id + 1, into_branch_id + 1

    @classmethod
    def delete_in_branch(cls, branch_id):
        cls.objects(branch_id=branch_id).delete()

    @classmethod
    def delete_in_branches(cls, branches_ids):
        cls.objects(branch_id__in=branches_ids).delete()
