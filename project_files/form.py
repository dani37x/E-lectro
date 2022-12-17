from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired, Length


class UserCreate(FlaskForm):
  nickname = StringField(description='nickname', validators=[DataRequired(), Length(max=30)])
  first_name = StringField(description='first_name', validators=[DataRequired(), Length(max=20)])
  surname = StringField(description='surname', validators=[DataRequired(), Length(max=30)])
  email = EmailField(description='e-mail', validators=[DataRequired(), Length(max=50)])
  password = PasswordField(description='password', validators=[DataRequired(), Length(min=9, max=20)])
  submit = SubmitField('submit')

