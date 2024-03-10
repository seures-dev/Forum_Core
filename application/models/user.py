from flask_login import UserMixin
from mongoengine import Document, StringField, EmailField, DateField, BooleanField, IntField
from datetime import date


class User(Document, UserMixin):

    user_id = StringField(required=True)
    _int_id = IntField(default=0)
    nickname = StringField(required=True)
    email = EmailField(required=True)
    phone = StringField()
    password = StringField(required=True)
    create_time = DateField(required=True, default=date.today())
    confirmation = BooleanField(required=True)
    avatar = StringField()
    title = StringField()
    access_level = IntField(default=0)
    post_count = IntField(default=0)
    branch_count = IntField(default=0)
    thread_count = IntField(default=0)
    carma = IntField(default=0)

    @property
    def int_id(self):
        return self._int_id

    @int_id.setter
    def int_id(self, value):
        if self._int_id == 0:
            self._int_id = value
            return
        raise ValueError("Field already set and can't be changed")


    def get_nickname(self):
        return self.nickname

    def get_avatar(self):
        if self.avatar:
            return self.avatar
        return "img/default_avatar.png"

    def get_id(self):
        return self.user_id
