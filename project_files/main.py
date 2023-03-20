from project_files import app
from project_files import db
from project_files import login_manager
from project_files import SESSIONS, EVENTS, DATA
from project_files import queue

from flask_login import login_required, current_user
from flask import render_template, url_for, redirect, request, session, make_response

from .database import User, Blocked, Product

from .scripts.functions import check_admin, check_user, user_searched, recently_searched
from .scripts.functions import delete_expired_data, similar_products_to_queries
from .scripts.functions import classification, save_event

from datetime import datetime

import random


@login_manager.user_loader
def load_user(user_id):
    
    try:
        return User.query.get(user_id)
    
    except Exception as e:
        save_event(event=e, site='login manager')


@app.before_first_request
def before_first_request():
  pass
  # db.create_all()


@app.before_request
def before_request():

  minutes = ['5', '20', '30','45', '50']

  if str(datetime.now().minute) in minutes:
    queue.enqueue(delete_expired_data, d=0, h=0, m=15, file_path=SESSIONS)
    queue.enqueue(delete_expired_data, d=7, h=0, m=0, file_path=EVENTS)
    queue.enqueue(delete_expired_data, d=7, h=0, m=0, file_path=DATA)


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

    if len(queryset) > 3:

      user_searched(
        username=current_user.username,
        ip=request.remote_addr,
        searched=queryset
      )

  return render_template(
    'page.html',
    products=products,
    user=current_user.username,
    recently_searched=recently_searched(),
    similar_products_to_queries=similar_products_to_queries(username=current_user.username),
  )


@app.route('/shop/category', methods=['GET', 'POST'])
def category():

  products = Product.query.all()
  categories = []
  for product in products:
    if product.category not in categories:
      categories.append(product.category)

  return render_template('category.html', categories=categories)


@app.route('/shop/<category>/products', methods=['GET', 'POST'])
def products(category):

  products = Product.query.filter_by(category=category)

  if category in request.cookies:

    money = request.cookies.get(category)
    type_of_user = classification(category=category, money=money)

    products_for_user = []
    the_others = []

    for product in products:

      if classification(category=product.category, money=product.price) == type_of_user:
        products_for_user.append(product)
        
      else:
        the_others.append(product)

    random.shuffle(the_others)

    products_for_user.extend(the_others)
    
    return render_template('products.html', products=products_for_user)
  
  return render_template('products.html', products=products)


@app.route('/shop/products/<product_id>', methods=['GET', 'POST'])
def product_info(product_id):

  product = Product.query.filter_by(id=product_id).first()

  resp = make_response(render_template('product_info.html', product=product))

  resp.set_cookie(f'{product.category}', f'{product.price}')
  
  # print(request.cookies.get(f'{product.category}'))
  return resp


@app.route('/shop/api', methods=['GET', 'POST'])
@login_required
def shop_api():

  list_of_products = []

  products = Product.query.all()

  for product in products:

    data = {}
    data['name'] = product.name
    data['category'] = product.category
    data['company'] = product.company
    data['price'] = product.price

    list_of_products.append(data)
    
  return list_of_products


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
  #       active=True,
  #       points=1000,
  #       newsletter=True,
  #     )
  #     db.session.add(user)
  #     db.session.commit()
  # except Exception as e:
  #   print(e)
  # print(send_newsletter())
  return 'x'
