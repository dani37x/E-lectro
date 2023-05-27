"""
The "background.py" file is a collection of functions designed to operate
automatically without the need for human intervention. These functions
include the ability to delete expired data from JSON files, unblock users
after specific time who have been blocked, and set previous prices after a
discount or price hike has ended.

Additionally, the file includes views for displaying captchas and canceling
tasks from the Redis queue and recorder.
"""

from project_files import app
from project_files import scheduler
from project_files import SESSIONS, EVENTS, DATA, PRICES
from project_files import session
from project_files import job_registry
from project_files import session
from project_files import redis_instance

from flask_login import login_required, current_user
from flask import render_template, url_for, redirect, request

from .form import CharsCounter

from .scripts.functions import save_event, check_user, check_admin
from .scripts.functions import generator, random_char, unblock
from .scripts.functions import delete_expired_data, save_event, failed_captcha
from .scripts.functions import end_of_promo

from .scripts.actions import block_users

from rq.job import cancel_job
from rq.command import send_stop_job_command


scheduler.add_job(
  unblock, 
  trigger='interval', 
  hours=12,
)
scheduler.add_job(
  delete_expired_data, 
  args=[0, 0, 20, SESSIONS], 
  trigger='interval', 
  minutes=15
)
scheduler.add_job(
  delete_expired_data, 
  args=[5, 0, 0, EVENTS], 
  trigger='interval', 
  minutes=10
)
scheduler.add_job(
  delete_expired_data, 
  args=[7, 0, 0, DATA], 
  trigger='interval', 
  hours=1
)
scheduler.add_job(
  delete_expired_data, 
  args=[1, 0, 0, PRICES], 
  trigger='interval', 
  days=30
)
scheduler.add_job(
  end_of_promo,
  trigger='interval', 
  days=1
)
scheduler.start()


@app.route('/captcha', methods=['GET', 'POST'])
@login_required
# @check_user('captcha')
def captcha():

  try:
    if failed_captcha(username=current_user.username):
        block_users([current_user.id])
        return redirect( url_for('logout'))

    session['chances'] = session['chances'] - 1

    if session.get('chances') < 0 or session.get('chances') == None:
      save_event(
        event=f'The user {current_user.username} was not passed the captcha',
        site=captcha.__name__
      )
      return redirect( url_for('logout'))
    

    prohibited_chars = [
      'i', 'l', '_', '-', '`', '"', '=', '.', ',', '>', '{', ')'
    ]
    answer = random_char(without=prohibited_chars)
    obstacle = random_char(disabled_char=answer, without=prohibited_chars)
    data = generator(answer=answer, obstacle=obstacle)
    form = CharsCounter()
    current_chance = session.get('chances')
    session[f'chance {current_chance}'] = data['answer_count']

    if request.method == 'POST':

      if form.validate_on_submit():
        chars = form.chars.data
        if chars == session[f'chance {current_chance+1}']:
          session['chances'] = 4
          session['captcha_completed'] = True
          return redirect( url_for(session.get('previous_site','login')))
        
        else:
          if session.get('chances') != 0:
            session['chances'] = session['chances'] + 1
          return redirect( url_for('captcha'))
        
  except Exception as e:
    save_event(event=e, site=captcha.__name__)
    return redirect( url_for('login'))

  return render_template('captcha/captcha.html', form=form, data=data, answer=answer)


@app.route('/cancel/<task_id>', methods=['GET', 'POST'])
@login_required
# @check_user('admin')
# @check_admin('admin')
def cancel_task(task_id):
  
  try:
    send_stop_job_command(redis_instance, task_id)

    save_event(
      event=f'task {task_id} was canceled',
      site=cancel_task.__name__
    )

    for job_id in job_registry.get_job_ids():
        job_registry.remove(job_id)
        save_event(
          event=f'The task {task_id} was deleted from registry',
          site=cancel_task.__name__
        )

    if session['previous_site'] != 'nothing':
      return redirect( url_for(session.get('previous_site','nothing')))
  
    else:
      return redirect( url_for('admin'))

  except Exception as e:
    save_event(event=e, site=cancel_job.__name__)
    return 'error with cancel job'