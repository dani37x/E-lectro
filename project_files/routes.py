from project_files import app
from project_files import db
from project_files import login_manager

from flask_login import login_user, logout_user, login_required, current_user

from flask import Flask, render_template, url_for, redirect, flash, request

from .form import UserCreator, UserLogin

from .database import User


@app.before_first_request
def before_first_request():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/', methods=['GET', 'POST'])
@login_required
def page():

  return render_template('page.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
  form = UserLogin()
  if form.validate_on_submit():
    user = User.query.filter_by(username=form.username.data).first()
    if user:
      user = User.query.filter_by(email=form.email.data).first()
      if user:
        user = User.query.filter_by(password=form.password.data).first()
        if user:
          login_user(user, remember=True)
          return redirect( url_for('page'))
  return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
  form = UserCreator()
  if form.validate_on_submit():
    username = form.username.data
    first_name = form.first_name.data
    surname = form.surname.data
    email = form.email.data
    password = form.password.data
    user = UserCreator(
      username=username,
      first_name=first_name,
      surname=surname,
      email=email,
      password=password
    )
    db.session.add(user)
    db.session.commit()
    return redirect( url_for('login'))
  return render_template('register.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('login')

@app.errorhandler(404)
def handle_404(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def handle_500(e):
    return render_template('500.html'), 500