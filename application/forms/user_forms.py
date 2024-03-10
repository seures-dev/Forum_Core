from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from ..models.user import User
from application.models.redis_service import RedisSerializer


class Validator:
    def __init__(self, model, field, message):
        self.model = model
        self.field = field
        self.message = message


class Unique(Validator):

    def __init__(self, model, field, message):
        super().__init__(model, field, message)

    def __call__(self, form, field):
        check = self.model.objects(**{self.field.name: field.data}).first()
        if check:
            raise ValidationError(self.message)


class Contain(Validator):
    def __init__(self, model, field, message):
        super().__init__(model, field, message)

    def __call__(self, form, field):
        check = self.model.objects(**{self.field.name: field.data}).first()

        if not check:
            raise ValidationError(self.message)


class AlreadySent(Validator):
    def __init__(self, model, field, message):
        super().__init__(model, field, message)

    def __call__(self, form, field):
        check = RedisSerializer.get_value(f"TMP-forgot:{field.data}")
        if check:
            raise ValidationError(self.message)


class Forgot(FlaskForm):
    ''' User forgot password form. '''
    email = StringField('Email address', validators=[
        DataRequired(), Email(),
        AlreadySent(None, None, 'Message for restore your password already sent on your email, check your mail'),
        Contain(User, User.email, 'Account with this email not exist'),
    ])


class Reset(FlaskForm):
    ''' User reset password form. '''
    password = PasswordField('Password', validators=[
        DataRequired(), Length(min=6),
        EqualTo('confirm', message='Passwords must match.')
    ])
    confirm = PasswordField('Confirm password')


class Login(FlaskForm):
    ''' User login form. '''
    email = StringField('Email/Nickname', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class SignUp(FlaskForm):
    ''' User sign up form. '''
    nickname = StringField("Nickname", validators=[
        DataRequired(), Length(min=4),
        Unique(User, User.nickname, 'This nickname is already taken.')
    ])
    phone = StringField('Phone number', validators=[DataRequired(), Length(min=6)], default="+")
    email = StringField('Email address', validators=[
        DataRequired(), Email(),
        Unique(User, User.email, 'This email address is already linked to an account.')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(), Length(min=6),
        EqualTo('confirm', message='Passwords must match.')
    ])
    confirm = PasswordField('Confirm password')
