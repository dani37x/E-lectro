from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError

from .database import User

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
    
def existing_email(form, field):
  if field.data in User.query.filter(User.email).all():
      raise ValidationError('this email already exist')


class UserCreator(FlaskForm):
  username = StringField(
    description='nickname',
    validators=[
      DataRequired(),
      Length(max=30),
      existing_user,
    ])
  first_name = StringField(description='first_name', validators=[DataRequired(), Length(max=20)])
  surname = StringField(description='surname', validators=[DataRequired(), Length(max=30)])
  email = EmailField(description='e-mail',
   validators=[
      DataRequired(),
      Length(max=50),
      existing_email
    ])
  password = PasswordField(description='password', validators=[DataRequired(), password_checking])
  password_2 = PasswordField(
    description='repeat password',
    validators=[
      DataRequired(),
      Length(max=50),
      EqualTo('password'),
    ])


class UserLogin(FlaskForm):
    username = StringField(description='username', validators=[DataRequired(), Length(max=30)])
    email = EmailField(description='e-mail', validators=[DataRequired(), Length(max=50)])
    password = PasswordField(description='password', validators=[DataRequired(), Length(max=50)])
    remember = BooleanField(description='remember me')



class NewPassword(FlaskForm):
    username = StringField(description='username', validators=[DataRequired(), Length(max=30)])
    current_password = PasswordField(description='current password', validators=[DataRequired()])
    password = PasswordField(description='password', validators=[DataRequired()])
    password_2 = PasswordField(description='repeat password', validators=[
      DataRequired(),
      EqualTo('password'),
      password_checking
    ])
    
class RemindPassword(FlaskForm):
    username = StringField(description='username', validators=[DataRequired(), Length(max=30)])
    email = EmailField(description='e-mail', validators=[DataRequired(), Length(max=50)])