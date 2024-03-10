
from mongoengine import Document, StringField, DateTimeField, IntField, ObjectIdField, DictField, BooleanField
from bson import ObjectId
from datetime import datetime
from ..models.user import User as USerModel
class Thread(Document):
    thread_id = IntField(unique=True)
    name = StringField()
    pinned_thread = BooleanField(default=False)
    description = StringField()
    creator = DictField(field=StringField())
    created = DateTimeField(default=datetime.now())
    lasts_post = ObjectIdField()
    moderators = DictField(field=StringField())
    moderators_count = IntField()
    branch_count = IntField(default=0)
    image = StringField()

    # meta = {
    #     "indexes": [
    #         {"fields": ["thread_id"], "unique": True}
    #     ]
    # }

    def __init__(self, name, description, creator, **kwargs):
        super(Thread, self).__init__(**kwargs)
        self.name = name
        if description:
            self.description = description
        else:
            if creator is None:
                self.description = name + " thread"
            else:
                creator_id = list(creator.values())[0]
                self.description = name + " created by " + USerModel.objects(user_id=creator_id).first().nickname

        self.creator = creator

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
    def get_thread_by_id(cls, thread_id):
        thread = cls.objects.filter(thread_id=thread_id).first()
        if thread:
            return thread.to_dict()
        return None

    @classmethod
    def get_threads_with_offset(cls, offset) -> list['Thread']:
        threads = cls.objects.order_by("thread_id").skip(offset).limit(30).all()
        return [x.to_dict() for x in threads]

    @classmethod
    def count_threads(cls):
        return cls.objects.count()

    @classmethod
    def get_next_thread_id(cls):
        thread = cls.objects.order_by("-thread_id").limit(1).first()
        return thread.thread_id + 1

    @classmethod
    def increase_branch_count(cls, thread_id):
        cls.objects.filter(thread_id=thread_id).first().branch_count += 1

    @classmethod
    def decrease_branch_count(cls, thread_id):
        cls.objects.filter(thread_id=thread_id).first().branch_count -= 1


    @classmethod
    def delete_by_thread_id(cls, thread_id):
        thread = cls.objects.filter(thread_id=thread_id).first()
        if thread:
            thread.delete()
            return True
        return False