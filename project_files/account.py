from project_files import app
from project_files import db
from project_files import login_manager

from flask_login import login_user, logout_user, login_required, current_user
from flask import render_template, url_for, redirect, request, abort, session

from .form import UserCreator, UserLogin, RemindPassword, NewPassword

from .database import User, Blocked

from .scripts.functions import check_user, check_admin, max_reminders, unblock, save_error

from .scripts.actions import  message




@app.route('/login', methods=['GET', 'POST'])
def login():

  form = UserLogin()

  if form.validate_on_submit():

    user = User.query.filter_by(
      email=form.email.data,
      password=form.password.data,
      username=form.username.data
    ).first()

    if user:

      wheter_blocked = Blocked.query.filter_by(username=user.username).first()
      if wheter_blocked:

        if unblock(blocked_user=wheter_blocked):

          login_user(user, remember=form.remember.data)
          return redirect( url_for('page'))

        else:
          return abort(403)

      login_user(user, remember=form.remember.data)
      return redirect( url_for('page'))

  return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
  form = UserCreator()

  if form.validate_on_submit():

    user = User(
      username=form.username.data,
      first_name=form.first_name.data,
      surname=form.surname.data,
      email=form.email.data,
      password=form.password.data,
      ip=request.remote_addr,
      account_type='user',
      active=True
    )

    try:
      db.session.add(user)
      db.session.commit()
      
      try:
        message(kind='register', sender='electro@team.com', recipents=form.email.data)
      except Exception as e:
        print(e)
        return 'Errow with mail'

      return redirect( url_for('login'))

    except Exception as e:
      save_error(error=e, site=register.__name__)
      return 'xd'

  return render_template('register.html', form=form)


@app.route("/logout")
# @check_user('logout')
@login_required
def logout():
    logout_user()
    return redirect('login')


@app.route("/remind_password", methods=['GET', 'POST'])
# @check_user('remind_password')
def remind_password():

    form = RemindPassword()

    if form.validate_on_submit():

      user = User.query.filter_by(username=form.username.data).first()
      if user:
          user = User.query.filter_by(email=form.email.data).first()
          if user:
            if max_reminders():

              try:
                message(kind='password',sender='electro@team.com', recipents=form.email.data)
                return redirect( url_for('new_password'))

              except Exception as e:
                save_error(error=e, site=remind_password.__name__)
                return 'Error with mail'

            else:
              abort(403)

    return render_template('remind_password.html', form=form)


@app.route("/new_password", methods=['GET', 'POST'])
# @check_user('new_password')
def new_password():

    form = NewPassword()

    if form.validate_on_submit():

        user = User.query.filter_by(username=form.username.data).first()
        if user:
            user = User.query.filter_by(password=form.current_password.data).first()
            if user:
                user.password = form.password.data

                try:
                    db.session.commit()
                    return redirect( url_for('logout'))
                    
                except Exception as e:
                  save_error(error=e, site=new_password.__name__)
                  return 'Error with password chaning'

    return render_template('new_password.html', form=form)
