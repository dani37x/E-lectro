from project_files import app
from project_files import db
from project_files import login_manager

from flask_login import login_user, logout_user, login_required, current_user

from flask import Flask, render_template, url_for, redirect, flash, request, abort

from .form import UserCreator, UserLogin

from .database import User, Blocked

from.functions import checker

from .actions import delete_rows


@app.before_first_request
def before_first_request():
    db.create_all()
    user = Blocked(username='mama', ip='127.0.0.1')
    db.session.add(user)
    db.session.commit()
    # checker(username=current_user.username)


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

  return render_template('admin.html')

@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def admin_user():
  #if current_user.username != 'mama':
  #   abort(404)
  users = User.query.all() 
  if request.method == 'POST':
    data = request.form.getlist('id')
    selected_action = request.form['action']
    if selected_action == 'delete user':
      delete_rows(User, data)
      return redirect( url_for('admin_user'))
  
  return render_template('admin_user.html', users=users)


@app.route('/admin/blocked', methods=['GET', 'POST'])
@login_required
def admin_blocked():
  #if current_user.username != 'mama':
  #   abort(404)
  blocked = Blocked.query.all() 
  if request.method == 'POST':
    data = request.form.getlist('id')
    selected_action = request.form['action']
    if selected_action == 'delete user':
      delete_rows(Blocked, data)
      return redirect( url_for('admin_blocked'))



    # print(data)
    # blocked = 
  
  return render_template('admin_blocked.html', blocked=blocked)


@app.route('/update-user/<int:id>', methods=['GET', 'POST'])
def update_user(id):
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
      return redirect(url_for('admin_user'))
    except Exception as e:
      return 'xd'
  else:
    return render_template('update_user.html', user=user )


@app.route('/delete-user/<int:id>')
def delete_user(id):

  name_to_delete = User.query.get_or_404(id)
  try:
    db.session.delete(name_to_delete)
    db.session.commit()
    return redirect(url_for('admin_user'))
  except Exception as e:
    return 'xd'


@app.route('/update-blocked/<int:id>', methods=['GET', 'POST'])
def update_blocked(id):
  blocked = Blocked.query.get_or_404(id)
  if request.method == 'POST':
    blocked.username = request.form['username']
    blocked.ip = request.form['ip']
    try:
      db.session.commit()
      return redirect(url_for('admin_blocked'))
    except Exception as e:
      return 'xd'
  else:
    return render_template('update_blocked.html', blocked=blocked )

@app.route('/delete-blocked/<int:id>')
def delete_blocked(id):

  name_to_delete = Blocked.query.get_or_404(id)
  try:
    db.session.delete(name_to_delete)
    db.session.commit()
    return redirect(url_for('admin_blocked'))
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