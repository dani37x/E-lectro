from project_files import app
from project_files import db
from project_files import login_manager
from project_files import SESSIONS

from flask_login import login_user, logout_user, login_required, current_user
from flask import render_template, url_for, redirect, request, abort, session

from .form import UserCreator, UserLogin, RemindPassword, NewPassword, Key

from .database import User, Blocked

from .scripts.functions import check_user, check_admin, unblock, save_error
from .scripts.functions import check_session, random_string, string_to_date
from .scripts.functions import open_json, save_json

from .scripts.actions import  message

from datetime import datetime, timedelta



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


@app.route("/logout")
# @check_user('logout')
@login_required
def logout():
    logout_user()
    return redirect('login')


@app.route("/remind", methods=['GET', 'POST'])
def remind():
    
  form = RemindPassword()
  
  if request.method == 'POST':

    if form.validate_on_submit():
        
      user = User.query.filter_by(
            username=form.username.data,
            email=form.email.data
        ).first()
        
      if user:
    
        session_list = open_json(file_path=SESSIONS)
        
        sess = check_session(session_list=session_list)    
        key = random_string(size=6)
        
        session_list.append({
                "username": f"{form.username.data}",
                "time": f"{str(datetime.now().strftime('%d-%m-%Y  %H:%M:%S'))}",
                "session": f"{sess}",
                "key": f"{key}"
            })

        try:
          pass
          # message(kind='code', sender='Electro@team.com', recipents=[form.email.data], key=key)

        except Exception as e:
          save_error(error=e, site=remind.__name__)
          return 'xd'

        save_json(file_path=SESSIONS, data=session_list)

        return redirect( url_for( 'hash_session', rendered_session=sess))

  return render_template('remind_password.html', form=form)



@app.route('/password/<rendered_session>', methods=['GET', 'POST'])
def hash_session(rendered_session):

  form = Key()
  
  if request.method == 'POST':
  
    if form.validate_on_submit():

      session_list = open_json(file_path=SESSIONS)
          
      durabity = datetime.now() - timedelta(minutes=15)   
      active_sessions = [sess for sess in session_list if string_to_date(sess['time']) > durabity]

      save_json(file_path=SESSIONS, data=active_sessions)

      for sess in active_sessions:
          if sess['key'] == form.key.data and rendered_session == sess['session']:
              session['username'] = sess['username']
              return redirect( url_for('new_password', rendered_session=rendered_session))

      return redirect( url_for('remind'))

  return render_template('hash.html',  form=form)


@app.route('/new_password/<rendered_session>', methods=['GET', 'POST'])
def new_password(rendered_session):
    
  form = NewPassword()

  try:
    # essential line*
    if session['username']:
    
      if request.method == 'POST':

        if form.validate_on_submit():
        
            user = User.query.filter_by(username=session['username']).first()
            user.password = form.password.data
            db.session.commit()
            session.pop('username', None)
            return redirect( url_for('page'))
            
      return render_template('new_password.html', form=form)
    else:
        return redirect('remind')    

  except Exception as e:
    save_error(error=e, site=new_password.__name__)
    return 'nice try :)'
  
    