from project_files import app
from project_files import db

from flask_login import login_required, current_user
from flask import render_template, url_for, redirect, request


from .database import User, Blocked, Product

from .scripts.functions import not_null, save_event, check_admin, check_user

from .scripts.actions import delete_rows, block_user, message, backup
from .scripts.actions import account_activation, account_deactivation
from .scripts.actions import delete_unactive_accounts




@app.route('/admin', methods=['GET', 'POST'])
@login_required
# @check_user('admin')
# @check_admin('admin')
def admin():
  return render_template('admin.html')


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
        account_activation(model=User, data=data)
      
      if selected_action == 'account deactivation':
        account_deactivation(model=User, data=data)

      if selected_action == 'delete unactive accounts':
        delete_unactive_accounts()
        

      if selected_action == 'test email':
        users_emails = []
        for id in data:
          user = User.query.filter_by(id=id).first()
          users_emails.append(user.email)
        message(kind='no-reply', sender=current_user.username, recipents=users_emails, key='')
      
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
      return render_template('admin_user.html', blocked=blocked)
      
    data = request.form.getlist('id')
    selected_action = request.form['action']

    try:
      if selected_action == 'delete user':
        delete_rows(Blocked, data)
        return redirect( url_for('admin_blocked'))
      
      if selected_action == 'backup':
        backup(Blocked)

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
      return render_template('admin_user.html', products=products)
      
    data = request.form.getlist('id')
    selected_action = request.form['action']

    try:
      if selected_action == 'delete products':
        delete_rows(Product, data)
        return redirect( url_for('admin_product'))
      
      if selected_action == 'backup':
        backup(Product)
        #flash message

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
      ip='127.0.0.1',
      account_type=not_null(request.form['account_type']),
      active=True
    )

    try:
      db.session.add(new_user)
      db.session.commit()

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
    active = not_null(request.form['active'])
    user.active = True if 'True' in active else False

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
    db.session.delete(name_to_delete)
    db.session.commit()
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
      date=not_null(request.form['date']),
    )

    try:
      db.session.add(new_blocked)
      db.session.commit()

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
    db.session.delete(name_to_delete)
    db.session.commit()
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
    )

    try:
      db.session.add(new_product)
      db.session.commit()

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
    db.session.delete(name_to_delete)
    db.session.commit()
    return redirect(url_for('admin_product'))

  except Exception as e:
    save_event(event=e, site=delete_product.__name__)
    return 'xd'    

