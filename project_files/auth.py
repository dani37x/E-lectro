from project_files import app
from project_files import db
from project_files import queue
from project_files import login_manager
from project_files import bcrypt
from project_files import SESSIONS

from .form import UserCreator, UserLogin, RemindPassword, NewPassword, Key

from .database import User, Blocked

from .scripts.functions import check_user, not_null, unblock, save_event, captcha
from .scripts.functions import check_session, random_string, open_json, save_json

from .scripts.actions import  message
from .scripts.actions import newsletter_activation, newsletter_deactivation

from flask_login import login_user, logout_user, login_required, current_user
from flask import render_template, url_for, redirect, request, abort, session

from datetime import datetime, timedelta


@app.route('/account', methods=['GET', 'POST'])
# @check_user('account')
@captcha('account')
@login_required
def account():

  session['username'] = current_user.username
  sess = random_string(size=39)
  user = User.query.filter_by(username=current_user.username).first()

  return render_template('account/account.html', sess=sess, newsletter=user.newsletter)


@app.route('/account/newsletter/register', methods=['GET', 'POST'])
# @check_user('register_newsletter')
@captcha('register_newsletter')
@login_required
def register_newsletter():

  newsletter_activation(username=current_user.username)

  return redirect( url_for('account'))


@app.route('/account/newsletter/unregister', methods=['GET', 'POST'])
# @check_user('unregister_newsletter')
@captcha('unregister_newsletter')
@login_required
def unregister_newsletter():

  newsletter_deactivation(username=current_user.username)

  return redirect( url_for('account'))


@app.route('/account/register', methods=['GET', 'POST'])
def register():

  form = UserCreator()

  if form.validate_on_submit():

    try:

      session_list = open_json(file_path=SESSIONS)
      sess = check_session(session_list=session_list)    
      key = random_string(size=6)

      session_list.append({
              "username": f"{form.username.data}",
              "first_name": f"{form.first_name.data}",
              "surname": f"{form.surname.data}",
              "email": f"{form.email.data}",
              "password": f"{bcrypt.generate_password_hash(form.password.data).decode('utf-8')}",
              "ip": f"{request.remote_addr}",
              "time": f"{str(datetime.now().strftime('%d-%m-%Y  %H:%M:%S'))}",
              "session": f"{sess}",
              "key": f"{key}"
          })

      save_json(file_path=SESSIONS, data=session_list)
      # message('register', 'electro@team.com', form.email.data, key)

      return redirect( url_for('register_session', rendered_session=sess))

    except Exception as e:

      save_event(event=e, site=register.__name__)
      return 'Error with add register sessions'

  return render_template('auth/register.html', form=form)


@app.route('/register/<rendered_session>', methods=['GET', 'POST'])
def register_session(rendered_session):

  form = Key()

  if request.method == 'POST':

    if form.validate_on_submit():
      session_list = open_json(file_path=SESSIONS)

      for sess in session_list:
        if sess['session'] == rendered_session and sess['key'] == form.key.data:
          user = User(
            username=sess['username'],
            first_name=sess['first_name'],
            surname=sess['surname'],
            email=sess['email'],
            password=sess['password'],
            ip=sess['ip'],
            account_type='user',
            active=True,
            points=0,
            newsletter=False,
            date=f"{str(datetime.now().strftime('%d-%m-%Y  %H:%M:%S'))}",
          )

          try:
            db.session.add(user)
            db.session.commit()
            return redirect( url_for('login'))

          except Exception as e:
            save_event(event=e, site=register.__name__)
            return 'Error with register' 

      return redirect( url_for('register'))

  return render_template('auth/hash.html', form=form)


@app.route('/account/login', methods=['GET', 'POST'])
def login():

  form = UserLogin()

  if request.method == 'POST':

    if form.validate_on_submit():

      user = User.query.filter_by(
        email=form.email.data,
        username=form.username.data
      ).first()

      if user and (bcrypt.check_password_hash(user.password, form.password.data)):
        wheter_blocked = Blocked.query.filter_by(username=user.username).first()

        if wheter_blocked:
          if unblock(blocked_user=wheter_blocked):
            login_user(user, remember=form.remember.data)
            session['chances'] = 4
            return redirect( url_for('page'))

          else:
            return abort(403)

        login_user(user, remember=form.remember.data)
        session['chances'] = 4
        return redirect( url_for('page'))

  return render_template('auth/login.html', form=form)


@app.route("/account/logout")
# @check_user('logout')
@login_required
def logout():
    try:
      if session['captcha_completed']:
        session['captcha_completed'] = None
      logout_user()
      return redirect('login')
    except:
      return redirect('login')
    

@app.route("/account/remind", methods=['GET', 'POST'])
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
        key = random_string(size=9)
        
        session_list.append({
                "username": f"{form.username.data}",
                "time": f"{str(datetime.now().strftime('%d-%m-%Y  %H:%M:%S'))}",
                "session": f"{sess}",
                "key": f"{key}"
            })

        try:
          pass
          # message('code', 'Electro@team.com', form.email.data, key)

        except Exception as e:
          save_event(event=e, site=remind.__name__)
          return 'xd'

        save_json(file_path=SESSIONS, data=session_list)

        return redirect( url_for( 'hash_session', rendered_session=sess))

  return render_template('auth/remind_password.html', form=form)



@app.route('/account/change/<rendered_session>', methods=['GET', 'POST'])
def hash_session(rendered_session):

  form = Key()
  
  if request.method == 'POST':
  
    if form.validate_on_submit():

      session_list = open_json(file_path=SESSIONS)

      for sess in session_list:
          if sess['key'] == form.key.data and rendered_session == sess['session']:
              session['username'] = sess['username']
              if len(sess['key']) == 9: 
                return redirect( url_for('new_password', rendered_session=rendered_session))
              elif len(sess['key']) == 6:
                return redirect( url_for('new_email', rendered_session=rendered_session))

      return redirect( url_for('remind'))

  return render_template('auth/hash.html',  form=form)


@app.route('/account/new_password/<rendered_session>', methods=['GET', 'POST'])
def new_password(rendered_session):
    
  form = NewPassword()

  try:
    # essential line*
    if session['username'] != None and session['username'] != '':
    
      if request.method == 'POST':

        if form.validate_on_submit():
        
          user = User.query.filter_by(username=session['username']).first()
          user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
          db.session.commit()
          session.pop('username', None)
          return redirect( url_for('login'))
            
      return render_template('auth/new_password.html', form=form)

    else:
        return redirect('remind')    

  except Exception as e:
    save_event(event=e, site=new_password.__name__)
    return 'nice try :)'
  

@app.route('/account/details', methods=['GET', 'POST'])
@login_required
# @check_user('account_details')
@captcha('account_details')
def account_details():

  user = User.query.get_or_404(current_user.id)

  if request.method == 'POST':
  
    user.first_name = not_null(request.form['first_name'])
    user.surname = not_null(request.form['surname'])

    try:
      db.session.commit()
      save_event(
        event=f'The User {current_user.username} updated account details',
        site=account_details.__name__  
      )

    except Exception as e:
      save_event(event=e, site=account_details.__name__)
      return redirect( url_for('account_details'))

    try:
      username = not_null(request.form['username'])
      if username != user.username:

        if User.query.filter_by(username=username).first():
          #flash this username already exists
          return redirect( url_for('account_details'))
        
        else:
          user.username = username
          db.session.commit()
          save_event(
            event=f'The User {current_user.username} updated username to {username}',
            site=account_details.__name__  
          )

    except Exception as e:
      save_event(event=e, site=account_details.__name__)
      return redirect( url_for('account_details'))

    try:
      email = not_null(request.form['email'])
      if email != user.email:

        if User.query.filter_by(email=email).first():
          #flash this email already exists
          return redirect( url_for('account_details'))
        
        else:
          session_list = open_json(file_path=SESSIONS)
          sess = check_session(session_list=session_list)    
          key = random_string(size=6)
          session['new_email'] = email

          session_list.append({
            "username": f"{current_user.username}",
            "time": f"{str(datetime.now().strftime('%d-%m-%Y  %H:%M:%S'))}",
            "session": f"{sess}",
            "key": f"{key}"
          })
          
          # message('code', 'Electro@team.com', form.email.data, key)
          save_json(file_path=SESSIONS, data=session_list)
          
          return redirect( url_for('hash_session', rendered_session=sess))

    except Exception as e:
      save_event(event=e, site=account_details.__name__)
      return redirect( url_for('account_details'))
    
    return redirect( url_for('account_details'))
        
  else:
    return render_template('account/details.html', user=user)
  


@app.route('/account/new_email/<rendered_session>', methods=['GET', 'POST'])
def new_email(rendered_session):
    
  try:
    if session['username'] != None and session['username'] != '':
      
      if user := User.query.filter_by(username=session['username']).first():

        old_email = user.email
        user.email = session.get('new_email')
        db.session.commit()

        session.pop('username', None)
        session.pop('new_email', None)
        save_event(
          event=f'The User {current_user.username} updated email from {old_email} to {user.email}',
          site=account_details.__name__  
        )
        #flash email was updated
        return redirect( url_for('account_details'))

    else:
      return redirect('account') 
    
  except Exception as e:
    save_event(event=e, site=new_email.__name__)
    return redirect('account') 