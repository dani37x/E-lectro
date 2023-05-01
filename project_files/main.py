from project_files import app
from project_files import db
from project_files import login_manager

from .database import User, Blocked, Product
from sqlalchemy import desc, asc

from .scripts.functions import check_admin, check_user, captcha
from .scripts.functions import similar_products_to_queries, recently_searched
from .scripts.functions import classification, save_event, user_searched
from .scripts.functions import the_price

from flask_login import login_required, current_user
from flask import render_template, url_for, redirect, request, session, make_response

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
  db.create_all()


@app.before_request
def before_request():
  pass


@app.route('/', methods=['GET', 'POST'])
@login_required
@captcha('page')
def page():

  products = Product.query.all()

  if request.method == 'POST':
    queryset = request.form['search']
    sort_type = request.form['sort_type']

    products = (
      Product.query.filter(
        Product.name.contains(queryset) |
        Product.category.contains(queryset) |
        Product.company.contains(queryset)
      ).order_by(
        desc(Product.name) if sort_type == 'desc_name' else \
        asc(Product.name) if sort_type == 'asc_name' else \
        desc(Product.category) if sort_type == 'desc_category' else \
        asc(Product.category) if sort_type == 'asc_category' else \
        desc(Product.company) if sort_type == 'desc_company' else \
        asc(Product.company) if sort_type == 'asc_company' else \
        desc(Product.price) if sort_type == 'desc_price' else \
        asc(Product.price) if sort_type == 'asc_price' else None
      ).all()
    )

    if len(queryset) > 3:
      user_searched(
        username=current_user.username,
        ip=request.remote_addr,
        searched=queryset
      )

  return render_template(
    'shop/page.html',
    products=products,
    user=current_user.username,
    recently_searched=recently_searched(),
    similar_products_to_queries=similar_products_to_queries(username=current_user.username),
  )


@app.route('/shop/category', methods=['GET', 'POST'])
@captcha('category')
def category():

  categories = db.session.query(Product.category.distinct()).all()
  categories = [str(category[0]) for category in categories]
  categories = list(categories)

  return render_template('shop/category.html', categories=categories)


@app.route('/shop/<category>/products', methods=['GET', 'POST'])
@captcha('products')
def products(category):

  list_of_products = Product.query.filter_by(category=category)

  if category in request.cookies:
    money = request.cookies.get(category)
    type_of_user = classification(category=category, money=money)
    products_for_user = []
    the_others = []

    for product in list_of_products:
      if classification(category=product.category, money=product.price) == type_of_user:
        products_for_user.append(product)
        
      else:
        the_others.append(product)

    random.shuffle(the_others)
    products_for_user.extend(the_others)
    return render_template('shop/products.html', list_of_products=products_for_user)
  
  return render_template('shop/products.html', list_of_products=list_of_products)


@app.route('/shop/products/<product_id>', methods=['GET', 'POST'])
@captcha('product_info')
def product_info(product_id):

  product = Product.query.filter_by(id=product_id).first()
  discount = the_price(product=product, price_type='the_highest_price')
  discount = round(product.price*100/discount, 0)


  resp = make_response(
    render_template(
      'shop/product_info.html', 
      product=product,
      discount=int(discount) if discount < 100 else None,
      the_lowest_price=the_price(product=product, price_type='the_lowest_price'),
      the_highest_price=the_price(product=product, price_type='the_highest_price')
  ))

  resp.set_cookie(
    key=f'{product.category}', 
    value=f'{product.price}',
    max_age=10*60*60*24
  )
  return resp


@app.route('/shop/api', methods=['GET', 'POST'])
@login_required
@captcha('shop_api')
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
