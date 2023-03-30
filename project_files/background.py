from project_files import app
from project_files import scheduler
from project_files import SESSIONS, EVENTS, DATA
from project_files import session
from project_files import job_registry
from project_files import session
from project_files import redis_instance

from .scripts.functions import delete_expired_data, save_event

from flask_login import login_required, current_user
from flask import render_template, url_for, redirect, request

from .form import CharCounter

from .scripts.functions import save_event, check_user, check_admin
from .scripts.functions import  generator, random_char

from rq.job import cancel_job
from rq.command import send_stop_job_command


scheduler.add_job(delete_expired_data, args=[0, 0, 20, SESSIONS], trigger='interval', minutes=15)
scheduler.add_job(delete_expired_data, args=[7, 0, 0, EVENTS], trigger='interval', hours=1)
scheduler.add_job(delete_expired_data, args=[7, 0, 0, DATA], trigger='interval', days=1)
scheduler.start()


@app.route('/captcha', methods=['GET', 'POST'])
@login_required
# @check_user('captcha')
def captcha():

  try:
    session['chances'] = session['chances'] - 1

    if session.get('chances') < 1 or session.get('chances') == None:
      save_event(
        event=f'The user {current_user.username} was not passed the captcha',
        site=captcha.__name__
      )
      return redirect( url_for('logout'))
    
    answer = random_char(every_char=False)
    obstacle = random_char(without_char=answer, every_char=False)
    data = generator(answer=answer, obstacle=obstacle)
    form = CharCounter()

    if request.method == 'POST':

      if form.validate_on_submit():

        chars = form.chars.data
        if chars == data['answer_count']:
          session['chances'] = '4'
          session['captcha_completed'] = True
          return redirect( url_for(session.get('previous_site','login')))
        
        else:
          session['chances'] = session['chances'] + 1
          return redirect( url_for('captcha'))
        
  except Exception as e:
    save_event(event=e, site=captcha.__name__)
    return redirect( url_for(session.get('previous_site','login')))


  return render_template('captcha.html', form=form, data=data, answer=answer)


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