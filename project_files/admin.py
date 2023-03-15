from project_files import app
from project_files import db
from project_files import queue
from project_files import job_registry
from project_files import session
from project_files import redis_instance

from flask_login import login_required, current_user
from flask import render_template, url_for, redirect, request, jsonify

from .database import User, Blocked, Product

from .scripts.functions import not_null, save_event, check_admin, check_user
from .scripts.functions import rq_add_row_to_db, rq_delete_db_row

from redis import Redis
from rq.job import Job, cancel_job
from rq.command import send_stop_job_command

from .scripts.actions import delete_rows, block_user, message, backup
from .scripts.actions import account_activation, account_deactivation
from .scripts.actions import delete_inactive_accounts, restore_database
from .scripts.actions import send_newsletter

from datetime import datetime



@app.route('/admin', methods=['GET', 'POST'])
@login_required
# @check_user('admin')
# @check_admin('admin')
def admin():
  return render_template('admin.html')


@app.route('/cancel/<task_id>', methods=['GET', 'POST'])
@login_required
# @check_user('admin')
# @check_admin('admin')
def cancel_task(task_id):
  # try:
    # job = Job.fetch(task_id, Redis())
    send_stop_job_command(Redis(), task_id)

    for job_id in job_registry.get_job_ids():
        job_registry.remove(job_id)

    if session['previous_site'] != 'nothing':
      return redirect( url_for(session.get('previous_site','nothing')))
  
    else:
      return redirect( url_for('admin'))

  # except Exception as e:

  #   save_event(event=e, site=cancel_job.__name__)
  #   return 'error with cancel job'
 

@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
# @check_admin('admin_user')
# @check_user('admin_user')
def admin_user():

  users = User.query.all() 

  if request.method == 'POST':

    searching = request.form['search']

    if searching != None and searching != '':

      users = (
        User.query.filter(User.username.contains(searching)
          | (User.first_name.contains(searching))
          | (User.surname.contains(searching))
          | (User.email.contains(searching))
          | (User.active.contains(searching))).all()
      )
      return render_template('admin_user.html', users=users)

    data = request.form.getlist('id')
    selected_action = request.form['action']

    try:
      if selected_action == 'delete user':
        delete_rows(User, data)
        return redirect( url_for('admin_user'))

      if selected_action == 'block user':
        block_user(data=data)

      if selected_action == 'account activation':

        task = queue.enqueue(account_activation, model=User, data=data)
        session['previous_site'] = admin_user.__name__
        return render_template('admin_user.html', users=users, task=task)
      
      if selected_action == 'account deactivation':

        task = queue.enqueue(account_deactivation, model=User, data=data)
        session['previous_site'] = admin_user.__name__
        return render_template('admin_user.html', users=users, task=task)

      if selected_action == 'delete unactive accounts':
        queue.enqueue(delete_inactive_accounts)

      if selected_action == 'restore database':
        restore_database(User)

      if selected_action == 'send newsletter':
        send_newsletter()

      if selected_action == 'test email':
        users_emails = []
        for id in data:
          user = User.query.filter_by(id=id).first()
          users_emails.append(user.email)

        queue.enqueue(message, 'no-reply', current_user.username, users_emails)
      
      if selected_action == 'backup':
        backup(User)

    except Exception as e:
      save_event(event=e, site=admin_user.__name__)
      return 'Error with actions'
  
  return render_template('admin_user.html', users=users)


@app.route('/admin/blocked', methods=['GET', 'POST'])
@login_required
# @check_admin('admin_blocked')
# @check_user('admin_blocked')
def admin_blocked():

  blocked = Blocked.query.all() 

  if request.method == 'POST':

    searching = request.form['search']
    if searching != None and searching != '':
      blocked = (
        Blocked.query.filter(User.username.contains(searching)
          | (Blocked.ip.contains(searching))).all()
      )
      return render_template('admin_blocked.html', blocked=blocked)
      
    data = request.form.getlist('id')
    selected_action = request.form['action']

    try:

      if selected_action == 'delete user':
        delete_rows(Blocked, data)
        return redirect( url_for('admin_blocked'))
      
      if selected_action == 'backup':
        backup(Blocked)

      if selected_action == 'restore database':
        restore_database(Blocked)

    except Exception as e:
      save_event(event=e, site=admin_blocked.__name__)
      return 'Error with actions'

  return render_template('admin_blocked.html', blocked=blocked)


@app.route('/admin/product', methods=['GET', 'POST'])
@login_required
# @check_admin('admin_product')
# @check_user('admin_product')
def admin_product():

  products = Product.query.all() 

  if request.method == 'POST':

    searching = request.form['search']
    if searching != None and searching != '':
      products = (
        Product.query.filter(Product.name.contains(searching)
          | (Product.category.contains(searching))
          | (Product.company.contains(searching))).all()
      )
      return render_template('admin_product.html', products=products)
      
    data = request.form.getlist('id')
    selected_action = request.form['action']

    try:
      if selected_action == 'delete products':
        delete_rows(Product, data)
        return redirect( url_for('admin_product'))
      
      if selected_action == 'backup':
        backup(Product)
        #flash message

      if selected_action == 'restore database':
        restore_database(Product)

    except Exception as e:
      save_event(event=e, site=admin_product.__name__)
      return 'Error with actions'

  return render_template('admin_product.html', products=products)


# admin operations like add, update, delete

@app.route('/add-user', methods=['GET', 'POST'])
@login_required
# @check_admin('add_user')
# @check_user('add_user')
def add_user():

  if request.method == 'POST':

    new_user = User(
      username=not_null(request.form['username']),
      first_name=not_null(request.form['first_name']),
      surname=not_null(request.form['surname']),
      email=not_null(request.form['email']),
      password=not_null(request.form['password']),
      ip=not_null(request.form['ip']),
      account_type=not_null(request.form['account_type']),
      active=True,
      points=not_null(request.form['points']),
      newsletter=False,
      date = f"{str(datetime.now().strftime('%d-%m-%Y  %H:%M:%S'))}",
    )

    try:
      queue.enqueue(rq_add_row_to_db, object=new_user)

    except Exception as e:
      save_event(event=e, site=add_user.__name__)
      return 'xd'

    return redirect( url_for('admin_user'))

  return render_template('add_user.html')


@app.route('/update-user/<int:id>', methods=['GET', 'POST'])
@login_required
# @check_admin('update_user')
# @check_user('update_user')
def update_user(id):

  user = User.query.get_or_404(id)

  if request.method == 'POST':

    user.username = not_null(request.form['username'])
    user.first_name = not_null(request.form['first_name'])
    user.surname = not_null(request.form['surname'])
    user.email = not_null(request.form['email'])
    user.password = not_null(request.form['password'])
    user.account_type = not_null(request.form['account_type'])
    user.points = not_null(request.form['points'])
    user.date = not_null(request.form['date'])
    newsletter = not_null(request.form['newsletter'])
    active = not_null(request.form['active'])
    
    
    user.active = True if 'True' in active or 'true' in active else False
    user.newsletter = True if 'True' in newsletter or 'true' in newsletter else False

    try:
      db.session.commit()
      return redirect( url_for('admin_user'))

    except Exception as e:
      save_event(event=e, site=update_user.__name__)
      return 'xd'
  
  else:
    return render_template('update_user.html', user=user )


@app.route('/delete-user/<int:id>')
@login_required
# @check_admin('delete_user')
# @check_user('delete_user')
def delete_user(id):

  name_to_delete = User.query.get_or_404(id)

  try:
    queue.enqueue(rq_delete_db_row, object=name_to_delete)

    return redirect(url_for('admin_user'))

  except Exception as e:
    save_event(event=e, site=delete_user.__name__)
    return 'xd'


@app.route('/add-blocked', methods=['GET', 'POST'])
@login_required
# @check_admin('add_blocked')
# @check_user('add_blocked')
def add_blocked():

  if request.method == 'POST':

    new_blocked = Blocked(
      username=not_null(request.form['username']),
      ip=not_null(request.form['ip']),
      date=f"{str(datetime.now().strftime('%d-%m-%Y  %H:%M:%S'))}",
    )

    try:
      queue.enqueue(rq_add_row_to_db, object=new_blocked)

    except Exception as e:
      save_event(event=e, site=add_blocked.__name__)
      return 'xd'

    return redirect( url_for('admin_blocked'))
  return render_template('add_blocked.html')


@app.route('/update-blocked/<int:id>', methods=['GET', 'POST'])
@login_required
# @check_admin('update_blocked')
# @check_user('update_blocked')
def update_blocked(id):

  blocked = Blocked.query.get_or_404(id)

  if request.method == 'POST':

    blocked.username = not_null(request.form['username'])
    blocked.ip = not_null( request.form['ip'])
    blocked.date = not_null( request.form['date'])

    try:
      db.session.commit()
      return redirect(url_for('admin_blocked'))

    except Exception as e:
      save_event(event=e, site=update_blocked.__name__)
      return 'xd'

  else:
    return render_template('update_blocked.html', blocked=blocked )


@app.route('/delete-blocked/<int:id>')
@login_required
# @check_admin('delete_blocked')
# @check_user('delete_blocked')
def delete_blocked(id):

  name_to_delete = Blocked.query.get_or_404(id)

  try:
    
    queue.enqueue(rq_delete_db_row, object=name_to_delete)

    return redirect(url_for('admin_blocked'))
  
  except Exception as e:
    save_event(event=e, site=delete_blocked.__name__)
    return 'xd'    


@app.route('/add-product', methods=['GET', 'POST'])
@login_required
# @check_admin('add_product')
# @check_user('add_product')
def add_product():

  if request.method == 'POST':

    new_product = Product(
      name=not_null(request.form['name']),
      category=not_null(request.form['category']),
      company=not_null(request.form['company']),
      price=not_null(request.form['price']),
      date=f"{str(datetime.now().strftime('%d-%m-%Y  %H:%M:%S'))}"
    )

    try:
      queue.enqueue(rq_add_row_to_db, object=new_product)

    except Exception as e:
      save_event(event=e, site=add_product.__name__)
      return 'xd'

    return redirect( url_for('admin_product'))

  return render_template('add_product.html')


@app.route('/update-product/<int:id>', methods=['GET', 'POST'])
@login_required
# @check_admin('update_product')
# @check_user('update_product')
def update_product(id):

  product = Product.query.get_or_404(id)
  if request.method == 'POST':
    product.name = not_null(request.form['name'])
    product.category = not_null(request.form['category'])
    product.company = not_null(request.form['company'])
    product.price = not_null(request.form['price'])
    product.date = not_null(request.form['date'])

    try:
      db.session.commit()
      return redirect( url_for('admin_product'))

    except Exception as e:
      save_event(event=e, site=update_product.__name__)
      return 'xd'

  else:
    return render_template('update_product.html', product=product )


@app.route('/delete-product/<int:id>')
@login_required
# @check_admin('delete_product')
# @check_user('delete_product')
def delete_product(id):

  name_to_delete = Product.query.get_or_404(id)

  try:
    queue.enqueue(rq_delete_db_row, object=name_to_delete)

    return redirect(url_for('admin_product'))

  except Exception as e:
    save_event(event=e, site=delete_product.__name__)

    return 'xd'    

