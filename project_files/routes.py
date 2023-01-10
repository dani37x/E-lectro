from project_files import app
from project_files import db
from project_files import login_manager

from flask_login import login_user, logout_user, login_required, current_user
from flask import render_template, url_for, redirect, flash, request, abort
from flask_mail import Message

from .form import UserCreator, UserLogin, RemindPassword, NewPassword

from .database import User, Blocked, Product

from .functions import check_admin, not_null, check_user

from .actions import delete_rows, block_user, message




@app.before_first_request
def before_first_request():
    db.create_all()
    user = Blocked(username='mama', ip='127.0.0.1')
    db.session.add(user)
    db.session.commit()
    # checker(username=current_user.username)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/', methods=['GET', 'POST'])
@login_required
# @check_user('page')
def page():
  return render_template('page.html')


# login, register, logout, remind password, new password


@app.route('/login', methods=['GET', 'POST'])
def login():
  form = UserLogin()
  if form.validate_on_submit():
    user = User.query.filter_by(username=form.username.data).first()
    if user:
      user = User.query.filter_by(email=form.email.data).first()
      if user:
        user = User.query.filter_by(password=form.password.data).first()
        if user:
          print(form.remember.data)
          login_user(user, remember=form.remember.data)
          return redirect( url_for('page'))

  return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
  form = UserCreator()

  if form.validate_on_submit():
    # username = form.username.data
    # first_name = form.first_name.data
    # surname = form.surname.data
    # email = form.email.data
    # password = form.password.data
    user = User(
      username=form.username.data,
      first_name=form.first_name.data,
      surname=form.surname.data,
      email=form.email.data,
      password=form.password.data,
      ip=request.remote_addr,
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
            try:
              message(kind='password',sender='electro@team.com', recipents=form.email.data)
            except Exception as e:
              return 'Error with mail'
            return redirect( url_for('new_password'))
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
                  print(e)
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
        users_emails= []
        for id in data:
          user = User.query.filter_by(id=id).first()
          users_emails.append(user.email)
        message(kind='no-reply', sender=current_user.username, recipents=users_emails)
        return redirect( url_for('admin_user'))
    except Exception as e:
      print(e)
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
    if selected_action == 'delete user':
      delete_rows(Blocked, data)
      return redirect( url_for('admin_blocked'))

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
    if selected_action == 'delete products':
      delete_rows(Product, data)
      return redirect( url_for('admin_product'))

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
      # account_type='user',
      active=True
    )
    try:
      db.session.add(new_user)
      db.session.commit()
    except Exception as e:
      print(e)
      return 'xd' + e
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
    # user.account_type = not_null(request.form[''account_type])
    active = not_null(request.form['active'])
    user.active = True if 'True' in active else False
    try:
      db.session.commit()
      return redirect( url_for('admin_user'))
    except Exception as e:
      print(e)
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
    print(e)
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
    )
    try:
      db.session.add(new_blocked)
      db.session.commit()
    except Exception as e:
      print(e)
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
    try:
      db.session.commit()
      return redirect(url_for('admin_blocked'))
    except Exception as e:
      print(e)
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
      print(e)
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
      print(e)
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
    print(e)
    return 'xd'    


# backup


@app.route('/backup', methods=['GET', 'POST'])
@login_required
# @check_admin('backup')
# @check_user('backup')
def backup():
  users = User.query.all()
  blocked = Blocked.query.all()
  return render_template('backup.html', users=users)


# error handlers 


@app.errorhandler(404)
def handle_404(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def handle_500(e):
    return render_template('500.html'), 500