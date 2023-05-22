from project_files import app
from project_files import db
from project_files import queue
from project_files import session
from project_files import bcrypt

from flask_login import login_required, current_user
from flask import render_template, url_for, redirect, request

from .database import Users, BlockedUsers, Products
from sqlalchemy import desc, asc

from .scripts.functions import check_admin, check_user, captcha
from .scripts.functions import save_event, the_price, save_price
from .scripts.functions import rq_add_row_to_db, rq_delete_db_row

from .scripts.actions import delete_rows, block_users, message, backup
from .scripts.actions import account_activation, account_deactivation
from .scripts.actions import delete_inactive_accounts, restore_database
from .scripts.actions import send_newsletter, the_price_actions
from .scripts.actions import discount, previous_price, price_hike

from .form import not_null

from rq import Retry

from datetime import datetime
 

@app.route('/admin', methods=['GET', 'POST'])
@login_required
# @check_user('admin')
# @check_admin('admin')
@captcha('admin')
def admin():
  return render_template('admin/admin.html')


@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
# @check_admin('admin_user')
# @check_user('admin_user')
@captcha('admin_user')
def admin_user():
  
  users = Users().all_rows 

  if request.method == 'POST':
    searching = request.form['search']
    sort_type = request.form['sort_type']

    users = (
      Users.query.filter(
        Users.username.contains(searching) |
        Users.first_name.contains(searching) |
        Users.surname.contains(searching) |
        Users.email.contains(searching) |
        Users.account_type.contains(searching)
      ).order_by(
        desc(Users.username) if sort_type == 'desc_username' else \
        asc(Users.username) if sort_type == 'asc_username' else \
        desc(Users.first_name) if sort_type == 'desc_first_name' else \
        asc(Users.first_name) if sort_type == 'asc_first_name' else \
        desc(Users.surname) if sort_type == 'desc_surname' else \
        asc(Users.surname) if sort_type == 'asc_surname' else \
        desc(Users.email) if sort_type == 'desc_email' else \
        asc(Users.email) if sort_type == 'asc_email' else \
        desc(Users.account_type) if sort_type == 'desc_account_type' else \
        asc(Users.account_type) if sort_type == 'asc_account_type' else None
      ).all()
    )
    
    data = request.form.getlist('id')
    selected_action = request.form['action']

    try:
      if selected_action == 'delete user':
        task = queue.enqueue(
          delete_rows,
          model=Users,
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
            model=Users,
            data=data,
            retry=Retry(max=3, interval=[10, 30, 60])
          )
        
        return render_template('admin/admin_user.html', users=users, task=task)
      
      if selected_action == 'account deactivation':
        task = queue.enqueue(
          account_deactivation,
          model=Users,
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
        for user_id in data:
          user = Users.query.filter_by(id=user_id).first()
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
        restore_database(model=Users)

      if selected_action == 'backup':
        backup(model=Users)

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

  blocked = BlockedUsers().all_rows

  if request.method == 'POST':
    searching = request.form['search']
    sort_type = request.form['sort_type']

    blocked = (
      BlockedUsers.query.filter(
        BlockedUsers.username.contains(searching) |
        BlockedUsers.ip.contains(searching)
      ).order_by(
        desc(BlockedUsers.username) if sort_type == 'desc_username' else \
        asc(BlockedUsers.username) if sort_type == 'asc_username' else \
        desc(BlockedUsers.ip) if sort_type == 'desc_ip' else \
        asc(BlockedUsers.ip) if sort_type == 'asc_ip' else None
      ).all()
    )
      
    data = request.form.getlist('id')
    selected_action = request.form['action']

    try:
      if selected_action == 'delete user':
        task = queue.enqueue(
          delete_rows,
          model=BlockedUsers,
          data=data,
          retry=Retry(max=3, interval=[10, 30, 60])
        )
        return render_template('admin/admin_blocked.html', blocked=blocked, task=task)
      
      if selected_action == 'backup':
        backup(model=BlockedUsers)

      if selected_action == 'restore database':
        restore_database(model=BlockedUsers)

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

  products = Products().all_rows

  if request.method == 'POST':
    searching = request.form['search']
    sort_type = request.form['sort_type']

    products = (
      Products.query.filter(
        Products.name.contains(searching) |
        Products.category.contains(searching) |
        Products.company.contains(searching)
      ).order_by(
        desc(Products.name) if sort_type == 'desc_name' else \
        asc(Products.name) if sort_type == 'asc_name' else \
        desc(Products.category) if sort_type == 'desc_category' else \
        asc(Products.category) if sort_type == 'asc_category' else \
        desc(Products.company) if sort_type == 'desc_company' else \
        asc(Products.company) if sort_type == 'asc_company' else \
        desc(Products.price) if sort_type == 'desc_price' else \
        asc(Products.price) if sort_type == 'asc_price' else None
      ).all()
    )
      
    data = request.form.getlist('id')
    percent = request.form['percent']
    selected_action = request.form['action']
    promo_days = request.form['promo_days']

    try:
      if selected_action == 'delete products':
        task = queue.enqueue(
          delete_rows,
          model=Products,
          data=data,
          retry=Retry(max=3, interval=[10, 30, 60])
        )
        return render_template('admin/admin_product.html', products=products, task=task)
      
      if selected_action == 'discount':
        task = queue.enqueue(
          discount,
          percent=percent,
          data=data,
          days=promo_days,
          retry=Retry(max=3, interval=[10, 30, 60]),
        )
        return render_template('admin/admin_product.html', products=products, task=task)

      if selected_action == 'price_hike':
        task = queue.enqueue(
          price_hike,
          percent=percent,
          data=data,
          days=promo_days,
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
      
      if selected_action == 'the_lowest_price':
        task = queue.enqueue(
          the_price_actions,
          data=data,
          price_type=selected_action,
          retry=Retry(max=3, interval=[10, 30, 60])
        )
        return render_template('admin/admin_product.html', products=products, task=task)

      if selected_action == 'the_highest_price':
        task = queue.enqueue(
          the_price_actions,
          data=data,
          price_type=selected_action,
          retry=Retry(max=3, interval=[10, 30, 60])
        )
        return render_template('admin/admin_product.html', products=products, task=task)

      if selected_action == 'the_random_price':
        task = queue.enqueue(
          the_price_actions,
          data=data,
          price_type=selected_action,
          retry=Retry(max=3, interval=[10, 30, 60])
        )
        return render_template('admin/admin_product.html', products=products, task=task)


      if selected_action == 'backup':
        backup(model=Products)
        #flash message

      if selected_action == 'restore database':
        restore_database(model=Products)

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

    new_user = Users(
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
    )

    try:
      queue.enqueue(
        rq_add_row_to_db, 
        obj=new_user,
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

  user = Users.query.get_or_404(id)
  
  if request.method == 'POST':
    try:
      user.update_row(**dict(request.form))
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

  name_to_delete = Users.query.get_or_404(id)

  try:
    queue.enqueue(
      rq_delete_db_row, 
      obj=name_to_delete,
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
    new_blocked = BlockedUsers(
      username=username,
      ip=not_null(request.form['ip']),
    )

    try:
      queue.enqueue(
        rq_add_row_to_db, 
        obj=new_blocked,
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

  blocked = BlockedUsers.query.get_or_404(id)
  
  if request.method == 'POST':
    try:
      blocked.update_row(**dict(request.form))
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

  name_to_delete = BlockedUsers.query.get_or_404(id)

  try:
    queue.enqueue(
      rq_delete_db_row,
      obj=name_to_delete,
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
    new_product = Products(
      name=product,
      category=not_null(request.form['category']),
      company=not_null(request.form['company']),
      price=not_null(request.form['price']),
      old_price=not_null(request.form['old_price']),
    )

    try:
      queue.enqueue(
        rq_add_row_to_db, 
        obj=new_product,
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

  product = Products.query.get_or_404(id)

  if request.method == 'POST':

    try:
      product.update_row(**dict(request.form))
      save_price(product=product)
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

  name_to_delete = Products.query.get_or_404(id)

  try:
    queue.enqueue(
      rq_delete_db_row, 
      obj=name_to_delete,
      retry=Retry(max=3, interval=[10, 30, 60])
    )
    return redirect(url_for('admin_product'))

  except Exception as e:
    save_event(event=e, site=delete_product.__name__)
    return 'xd'    

