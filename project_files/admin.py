from project_files import app
from project_files import db
from project_files import queue
from project_files import session
from project_files import bcrypt

from flask_login import login_required, current_user
from flask import render_template, url_for, redirect, request

from .database import User, Blocked, Product

from .scripts.functions import check_admin, check_user, captcha
from .scripts.functions import not_null, save_event

from .scripts.actions import delete_rows, block_users, message, backup
from .scripts.actions import account_activation, account_deactivation
from .scripts.actions import delete_inactive_accounts, restore_database
from .scripts.actions import send_newsletter, discount, previous_price
from .scripts.actions import rq_add_row_to_db, rq_delete_db_row

from rq import Retry

from datetime import datetime
 

@app.route('/admin', methods=['GET', 'POST'])
@login_required
# @check_user('admin')
# @check_admin('admin')
def admin():

  session['previous_site'] = admin.__name__
  if session.get('captcha_completed', None) == None:
    return redirect( url_for('captcha'))

  return render_template('admin/admin.html')


@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
# @check_admin('admin_user')
# @check_user('admin_user')
@captcha('admin_user')
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
        task = queue.enqueue(
          delete_rows,
          model=User,
          data=data,
          retry=Retry(max=3, interval=[10, 30, 60])
        )
        return render_template('admin/admin_user.html', users=users, task=task)


      if selected_action == 'block users':
        task = queue.enqueue(
          block_users,
          data=data,
          retry=Retry(max=3, interval=[10, 30, 60])
        )
        return render_template('admin/admin_user.html', users=users, task=task)


      if selected_action == 'account activation':
        task = queue.enqueue(
          account_activation,
            model=User,
            data=data,
            retry=Retry(max=3, interval=[10, 30, 60])
          )
        
        return render_template('admin/admin_user.html', users=users, task=task)
      
      if selected_action == 'account deactivation':
        task = queue.enqueue(
          account_deactivation,
          model=User,
          data=data,
          retry=Retry(max=3, interval=[10, 30, 60])
        )
        return render_template('admin/admin_user.html', users=users, task=task)

      if selected_action == 'delete unactive accounts':
        task = queue.enqueue(
          delete_inactive_accounts,
          retry=Retry(max=3, interval=[10, 30, 60])  
        )
        return render_template('admin/admin_user.html', users=users, task=task)

      if selected_action == 'send newsletter':        
        task = queue.enqueue(
          send_newsletter,
          retry=Retry(max=3, interval=[10, 30, 60])
        )
        return render_template('admin/admin_user.html', users=users, task=task)

      if selected_action == 'test email':
        users_emails = []
        for id in data:
          user = User.query.filter_by(id=id).first()
          users_emails.append(user.email)

        task = queue.enqueue(
          message,
          'no-reply', 
          current_user.username, 
          users_emails,
          retry=Retry(max=3, interval=[50, 100, 200])
        )
        return render_template('admin/admin_user.html', users=users, task=task)

      if selected_action == 'restore database':
        restore_database(model=User)

      if selected_action == 'backup':
        backup(model=User)

    except Exception as e:
      save_event(event=e, site=admin_user.__name__)
      return 'Error with actions'
  
  return render_template('admin/admin_user.html', users=users)


@app.route('/admin/blocked', methods=['GET', 'POST'])
# @login_required
# @check_admin('admin_blocked')
# @check_user('admin_blocked')
# @captcha('admin_blocked')
def admin_blocked():

  blocked = Blocked.query.all() 

  if request.method == 'POST':
    searching = request.form['search']

    if searching != None and searching != '':
      blocked = (
        Blocked.query.filter(User.username.contains(searching)
          | (Blocked.ip.contains(searching))).all()
      )
      return render_template('admin/admin_blocked.html', blocked=blocked)
      
    data = request.form.getlist('id')
    selected_action = request.form['action']

    try:
      if selected_action == 'delete user':
        task = queue.enqueue(
          delete_rows,
          model=Blocked,
          data=data,
          retry=Retry(max=3, interval=[10, 30, 60])
        )
        return render_template('admin/admin_blocked.html', blocked=blocked, task=task)
      
      if selected_action == 'backup':
        backup(model=Blocked)

      if selected_action == 'restore database':
        restore_database(model=Blocked)

    except Exception as e:
      save_event(event=e, site=admin_blocked.__name__)
      return 'Error with actions'

  return render_template('admin/admin_blocked.html', blocked=blocked)


@app.route('/admin/product', methods=['GET', 'POST'])
@login_required
# @check_admin('admin_product')
# @check_user('admin_product')
@captcha('admin_product')
def admin_product():

  products = Product.query.all() 

  if request.method == 'POST':
    searching = request.form['search']
    print(len(searching))
    if searching != None and searching != '':
      products = (
        Product.query.filter(Product.name.contains(searching)
          | (Product.category.contains(searching))
          | (Product.company.contains(searching))).all()
      )
      return render_template('admin/admin_product.html', products=products)
      
    data = request.form.getlist('id')
    selected_action = request.form['action']

    try:
      if selected_action == 'delete products':
        task = queue.enqueue(
          delete_rows,
          model=Product,
          data=data,
          retry=Retry(max=3, interval=[10, 30, 60])
        )
        return render_template('admin/admin_blocked.html', products=products, task=task)
      
      if r'% discount' in selected_action:
        task = queue.enqueue(
          discount,
          percent=selected_action[0:2],
          data=data,
          retry=Retry(max=3, interval=[10, 30, 60])
        )
        return render_template('admin/admin_product.html', products=products, task=task)

      if selected_action == 'previous_price':
        task = queue.enqueue(
          previous_price,
          data=data,
          retry=Retry(max=3, interval=[10, 30, 60])
        )
        return render_template('admin/admin_product.html', products=products, task=task)

      if selected_action == 'backup':
        backup(model=Product)
        #flash message

      if selected_action == 'restore database':
        restore_database(model=Product)

    except Exception as e:
      save_event(event=e, site=admin_product.__name__)
      return 'Error with actions'

  return render_template('admin/admin_product.html', products=products)


# admin operations like add, update, delete


@app.route('/add-user', methods=['GET', 'POST'])
@login_required
# @check_admin('add_user')
# @check_user('add_user')
@captcha('add_user')
def add_user():

  if request.method == 'POST':

    password = not_null(request.form['password'])
    password = bcrypt.generate_password_hash(password).decode('utf-8')
    username = not_null(request.form['username'])

    new_user = User(
      username=username,
      first_name=not_null(request.form['first_name']),
      surname=not_null(request.form['surname']),
      email=not_null(request.form['email']),
      password=password,
      ip=not_null(request.form['ip']),
      account_type=not_null(request.form['account_type']),
      active=True,
      points=not_null(request.form['points']),
      newsletter=False,
      date = f"{str(datetime.now().strftime('%d-%m-%Y  %H:%M:%S'))}",
    )

    try:
      queue.enqueue(
        rq_add_row_to_db, 
        object=new_user,
        retry=Retry(max=3, interval=[10, 30, 60])
      )

      save_event(
        event=f'The {username} was added by {current_user.username}',
        site=add_user.__name__  
      )

    except Exception as e:
      save_event(event=e, site=add_user.__name__)
      return 'xd'

    return redirect( url_for('admin_user'))

  return render_template('admin/add_user.html')


@app.route('/update-user/<int:id>', methods=['GET', 'POST'])
@login_required
# @check_admin('update_user')
# @check_user('update_user')
@captcha('update_user')
def update_user(id):

  user = User.query.get_or_404(id)
  
  if request.method == 'POST':

    password = not_null(request.form['password'])
    password = bcrypt.generate_password_hash(password).decode('utf-8')

    user.username = not_null(request.form['username'])
    user.first_name = not_null(request.form['first_name'])
    user.surname = not_null(request.form['surname'])
    user.email = not_null(request.form['email'])
    user.password = password
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
    return render_template('admin/update_user.html', user=user )


@app.route('/delete-user/<int:id>')
@login_required
# @check_admin('delete_user')
# @check_user('delete_user')
@captcha('delete_user')
def delete_user(id):

  name_to_delete = User.query.get_or_404(id)

  try:
    queue.enqueue(
      rq_delete_db_row, 
      object=name_to_delete,
      retry=Retry(max=3, interval=[10, 30, 60])
    )
    return redirect(url_for('admin_user'))

  except Exception as e:
    save_event(event=e, site=delete_user.__name__)
    return 'xd'


@app.route('/add-blocked', methods=['GET', 'POST'])
@login_required
# @check_admin('add_blocked')
# @check_user('add_blocked')
@captcha('add_blocked')
def add_blocked():

  if request.method == 'POST':
    username = not_null(request.form['username'])
    new_blocked = Blocked(
      username=username,
      ip=not_null(request.form['ip']),
      date=f"{str(datetime.now().strftime('%d-%m-%Y  %H:%M:%S'))}",
    )

    try:
      queue.enqueue(
        rq_add_row_to_db, 
        object=new_blocked,
        retry=Retry(max=3, interval=[10, 30, 60])
      )

      save_event(
        event=f'{username} was added by {current_user.username}', 
        site=add_blocked.__name__
      )

    except Exception as e:
      save_event(event=e, site=add_blocked.__name__)
      return 'xd'

    return redirect( url_for('admin_blocked'))
  return render_template('admin/add_blocked.html')


@app.route('/update-blocked/<int:id>', methods=['GET', 'POST'])
@login_required
# @check_admin('update_blocked')
# @check_user('update_blocked')
@captcha('update_blocked')
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
    return render_template('admin/update_blocked.html', blocked=blocked )


@app.route('/delete-blocked/<int:id>')
@login_required
# @check_admin('delete_blocked')
# @check_user('delete_blocked')
@captcha('delete_blocked')
def delete_blocked(id):

  name_to_delete = Blocked.query.get_or_404(id)

  try:
    queue.enqueue(
      rq_delete_db_row,
      object=name_to_delete,
      retry=Retry(max=3, interval=[10, 30, 60])
    )
    return redirect(url_for('admin_blocked'))
  
  except Exception as e:
    save_event(event=e, site=delete_blocked.__name__)
    return 'xd'    


@app.route('/add-product', methods=['GET', 'POST'])
@login_required
# @check_admin('add_product')
# @check_user('add_product')
@captcha('add_product')
def add_product():

  if request.method == 'POST':
    product = not_null(request.form['name'])
    new_product = Product(
      name=product,
      category=not_null(request.form['category']),
      company=not_null(request.form['company']),
      price=not_null(request.form['price']),
      old_price=not_null(request.form['old_price']),
      date=f"{str(datetime.now().strftime('%d-%m-%Y  %H:%M:%S'))}"
    )

    try:
      queue.enqueue(
        rq_add_row_to_db, 
        object=new_product,
        retry=Retry(max=3, interval=[10, 30, 60])
      )

      save_event(
        event=f'The {product} was added by {current_user.username}', 
        site=add_product.__name__
      )

    except Exception as e:
      save_event(event=e, site=add_product.__name__)
      return 'xd'

    return redirect( url_for('admin_product'))

  return render_template('admin/add_product.html')


@app.route('/update-product/<int:id>', methods=['GET', 'POST'])
@login_required
# @check_admin('update_product')
# @check_user('update_product')
@captcha('update_product')
def update_product(id):

  product = Product.query.get_or_404(id)

  if request.method == 'POST':
    product.name = not_null(request.form['name'])
    product.category = not_null(request.form['category'])
    product.company = not_null(request.form['company'])
    product.price = not_null(request.form['price'])
    product.old_price = not_null(request.form['old_price'])
    product.date = not_null(request.form['date'])

    try:
      db.session.commit()
      return redirect( url_for('admin_product'))

    except Exception as e:
      save_event(event=e, site=update_product.__name__)
      return 'xd'
    
  else:
    return render_template('admin/update_product.html', product=product )


@app.route('/delete-product/<int:id>')
@login_required
# @check_admin('delete_product')
# @check_user('delete_product')
@captcha('delete_product')
def delete_product(id):

  name_to_delete = Product.query.get_or_404(id)

  try:
    queue.enqueue(
      rq_delete_db_row, 
      object=name_to_delete,
      retry=Retry(max=3, interval=[10, 30, 60])
    )
    return redirect(url_for('admin_product'))

  except Exception as e:
    save_event(event=e, site=delete_product.__name__)
    return 'xd'    

