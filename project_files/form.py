from project_files import disallowed_words
from .database import User

from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError

import string


def password_checking(form, field):
  if len(field.data) < 9 or len(field.data) > 20:
    raise ValidationError('Password must have minimum 9 length and maximum 20 length')
  punctuation = string.punctuation
  contain = False
  for char in punctuation:
    if char in field.data:
      contain = True
  if contain == False:
    raise ValidationError('Password must contain special char')
  uppercase = string.ascii_uppercase
  contain = False
  for char in uppercase:
    if char in field.data:
      contain = True
  if contain == False:
    raise ValidationError('Password must contain Big letter')
  lowercase = string.ascii_lowercase
  contain = False
  for char in lowercase:
    if char in field.data:
      contain = True
  if contain == False:
    raise ValidationError('Password must contain small letter')
  digits = string.digits
  contain = False
  for char in digits:
    if char in field.data:
      contain = True
  if contain == False:
    raise ValidationError('Password must contain number')


def existing_user(form, field):
  if field.data in User.query.filter(User.username).all():
      raise ValidationError('this username already exist')
  for word in disallowed_words:
    if word in field.data or word.upper() in field.data:
      raise ValidationError('element contains not allowed word')
    

def existing_email(form, field):
  if field.data in User.query.filter(User.email).all():
      raise ValidationError('this email already exist')
  for word in disallowed_words:
    if word in field.data or word.upper() in field.data:
      raise ValidationError('element contains not allowed word')


class UserCreator(FlaskForm):
  username = StringField('nickname',
    validators=[
      DataRequired(),
      Length(min=6, max=30),
      existing_user,
    ])
  first_name = StringField('first_name', validators=[DataRequired(), Length(min=2, max=20)])
  surname = StringField('surname', validators=[DataRequired(), Length(min=2, max=30)])
  email = EmailField('e-mail',
   validators=[
      DataRequired(),
      Length(min=4, max=20),
      existing_email
    ])
  password = PasswordField('password', validators=[DataRequired(), password_checking])
  password_2 = PasswordField('repeat password', 
    validators=[
      DataRequired(),
      Length(max=20),
      EqualTo('password'),
    ])


class UserLogin(FlaskForm):
  username = StringField('username', validators=[DataRequired()])
  email = EmailField('e-mail', validators=[DataRequired()])
  password = PasswordField('password', validators=[DataRequired()])
  remember = BooleanField('remember me')


class Key(FlaskForm):
  key = StringField('Enter the key', validators=[DataRequired(), Length(min=2, max=10)])


class NewPassword(FlaskForm):
  password = PasswordField('new password', validators=[DataRequired(), password_checking])
  password_2 = PasswordField('repeat password', validators=[
    DataRequired(),
    EqualTo('password'),
    password_checking
  ])
    

class RemindPassword(FlaskForm):
  username = StringField('username', validators=[DataRequired(), Length(max=30)])
  email = EmailField('e-mail', validators=[DataRequired(), Length(max=50)])


class CharsCounter(FlaskForm):
  chars = IntegerField(validators=[DataRequired()])