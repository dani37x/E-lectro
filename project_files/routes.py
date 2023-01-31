from project_files import app
from project_files import db
from project_files import login_manager

from flask_login import login_user, logout_user, login_required, current_user
from flask import render_template, url_for, redirect, flash, request, abort, session

from .form import UserCreator, UserLogin, RemindPassword, NewPassword

from .database import User, Blocked, Product

from .functions import check_admin, not_null, check_user, max_reminders, user_searched
from .functions import unblock, save_error

from .actions import delete_rows, block_user, message, backup



@app.before_first_request
def before_first_request():
    # db.create_all()
    session['remind_one'] = 'not set'
    session['remind_two'] = 'not set'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/test', methods=['GET', 'POST'])
def test():
  # try:
  #   user = Blocked(username='kekw', ip='127.0.0.1', date='1-1-2022')
  #   db.session.add(user)
  #   db.session.commit()
  #   for i in range(0,3):
  #     user = User(
  #       username=f'kekw{i}',
  #       first_name='kekw',
  #       surname='kekw',
  #       email=f'kekw@x{i}.pl',
  #       password='kekw!2@Kopyto',
  #       ip=f'192.15.24{i}',
  #       account_type='admin',
  #       active=True
  #     )
  #     db.session.add(user)
  #     db.session.commit()
  # except Exception as e:
  #   print(e)

  backup()

  return 'test'


@app.route('/', methods=['GET', 'POST'])
@login_required
# @check_user('page')
def page():
  products = Product.query.all()

  if request.method == 'POST':
    queryset = request.form['search']

    products = (
      Product.query.filter(Product.name.contains(queryset)
        | (Product.category.contains(queryset))
        | (Product.company.contains(queryset))).all()
    )

    if len(queryset) > 1:
      user_searched(
        username=current_user.username,
        ip=request.remote_addr,
        searched=queryset
      )

  return render_template('page.html', products=products, user=current_user.username)


@app.route('/info', methods=['GET', 'POST'])
@login_required
def second_page():
  return session.get('current', 'not set')
# login, register, logout, remind password, new password


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


# admin panel


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

      if selected_action == 'test email':
        users_emails = []
        for id in data:
          user = User.query.filter_by(id=id).first()
          users_emails.append(user.email)
        message(kind='no-reply', sender=current_user.username, recipents=users_emails)
      
      if selected_action == 'backup':
        backup(User)

    except Exception as e:
      save_error(error=e, site=admin_user.__name__)
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
      save_error(error=e, site=admin_blocked.__name__)
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
      save_error(error=e, site=admin_product.__name__)
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
      save_error(error=e, site=add_user.__name__)
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
      save_error(error=e, site=update_user.__name__)
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
    save_error(error=e, site=delete_user.__name__)
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
      save_error(error=e, site=add_blocked.__name__)
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
      save_error(error=e, site=update_blocked.__name__)
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
    save_error(error=e, site=delete_blocked.__name__)
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
      save_error(error=e, site=add_product.__name__)
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
      save_error(error=e, site=update_product.__name__)
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
    save_error(error=e, site=delete_product.__name__)
    return 'xd'    

