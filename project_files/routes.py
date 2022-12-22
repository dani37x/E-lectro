from project_files import app
from project_files import db
from project_files import login_manager

from flask_login import login_user, logout_user, login_required, current_user

from flask import Flask, render_template, url_for, redirect, flash, request, abort

from .form import UserCreator, UserLogin

from .database import User, Blocked

from.functions import checker




@app.before_first_request
def before_first_request():
    db.create_all()
    # user = Blocked(username='mama', ip='127.0.0.1')
    # db.session.add(user)
    # db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/', methods=['GET', 'POST'])
@login_required
def page():
  # checker(username=current_user.username)
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

    user = User(
      username=username,
      first_name=first_name,
      surname=surname,
      email=email,
      password=password,
      active = True
    )
    try:
      db.session.add(user)
      db.session.commit()
      return redirect( url_for('login'))
    except Exception as e:
      return 'xd'
  return render_template('register.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('login')


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
  # if current_user.username != 'mama':
  #   abort(404)
  
  users = User.query.all() 
  blocked = Blocked.query.all()

  return render_template('admin.html', users=users, blocked=blocked)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
  user = User.query.get_or_404(id)
  if request.method == 'POST':
    user.username = request.form['username']
    user.first_name = request.form['first_name']
    user.surname = request.form['surname']
    user.email = request.form['email']
    user.password = request.form['password']
    active = request.form['active']
    user.active = True if 'True' in active else False
    try:
      db.session.commit()
      return redirect(url_for('admin'))
    except Exception as e:
      return 'xd'
  else:
    return render_template("update.html", user=user )


@app.route('/delete/<int:id>')
def delete(object,id):
  objects = [Blocked, User]
  for i in objects:
    if str(i) == str(object):
      object = i
  name_to_delete = object.query.get_or_404(id)
  try:
    db.session.delete(name_to_delete)
    db.session.commit()
    return redirect(url_for('admin'))
  except Exception as e:
    return 'xd'


@app.route('/backup', methods=['GET', 'POST'])
@login_required
def backup():
  users = User.query.all()
  blocked = Blocked.query.all()
  return render_template('backup.html', users=users)


@app.errorhandler(404)
def handle_404(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def handle_500(e):
    return render_template('500.html'), 500