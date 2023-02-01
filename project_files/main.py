from project_files import app
from project_files import db

from flask_login import login_required, current_user
from flask import render_template, url_for, redirect, request, session


from .database import User, Blocked, Product

from .functions import check_admin, check_user, user_searched



@app.before_first_request
def before_first_request():
    # db.create_all()
    session['remind_one'] = 'not set'
    session['remind_two'] = 'not set'


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



