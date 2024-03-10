from flask_wtf import FlaskForm
from wtforms import StringField  #, FileField

from wtforms.validators import DataRequired, ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired


def validate_name(form, field):
    if field.data[0].isdigit():
        raise ValidationError('Name cannot start with a number.')



class ThreadForm(FlaskForm):
    name = StringField('Thread name', validators=[DataRequired(), validate_name])
    description = StringField('Thread description', validators=[DataRequired()])
    image = FileField('Thread image', validators=[])


class BranchForm(FlaskForm):
    name = StringField('Branch name', validators=[DataRequired(), validate_name])
    description = StringField('Branch description', validators=[DataRequired()])
    image = FileField('Branch image', validators=[])


class PostForm(FlaskForm):
    content = StringField('Content', validators=[DataRequired()])
    image = FileField('Post image', validators=[])



