"""
The "main.py" file is a central point whole project. Its destination is
subpages that are visible to customers of this shop. There are views
for categories and products. There are other features for the 
application as well, but only temporary. A new place will be found for them.
"""

from project_files import app
from project_files import db
from project_files import queue
from project_files import login_manager

from .database import Users, Products, UsersProducts
from sqlalchemy import desc, asc

from .scripts.functions import check_admin, check_user, captcha
from .scripts.functions import similar_products_to_queries, recently_searched
from .scripts.functions import classification, save_event, user_searched
from .scripts.functions import the_price, rq_add_row_to_db

from flask_login import login_required, current_user
from flask import render_template, url_for, redirect, request, session, make_response

from rq import Retry

from datetime import datetime

import random


@login_manager.user_loader
def load_user(user_id):
    try:
        return Users.query.get(user_id)
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

  products = Products.query.all()

  if request.method == 'POST':
    queryset = request.form['search']
    sort_type = request.form['sort_type']

    products = (
      Products.query.filter(
        Products.name.contains(queryset) |
        Products.category.contains(queryset) |
        Products.company.contains(queryset)
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

  categories = db.session.query(Products.category.distinct()).all()
  categories = [str(category[0]) for category in categories]
  categories = list(categories)

  return render_template('shop/category.html', categories=categories)


@app.route('/shop/<category>/products', methods=['GET', 'POST'])
@captcha('products')
def products(category):

  list_of_products = Products.query.filter_by(category=category)

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

  product = Products.query.filter_by(id=product_id).first()
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

  if request.method == 'POST':
    buy_product = UsersProducts(
      user_id=current_user.id,
      product_id=product.id,
      price=product.price
    )
    queue.enqueue(
      rq_add_row_to_db,
      obj=buy_product,
      retry=Retry(max=3, interval=[10, 30, 60])
    )
    # flash message
    return redirect( url_for('product_info', product_id=product_id))

  return resp


@app.route('/shop/api', methods=['GET', 'POST'])
@login_required
@captcha('shop_api')
def shop_api():

  list_of_products = []
  products = Products().all_rows

  for product in products:
    data = {}
    data['name'] = product.name
    data['category'] = product.category
    data['company'] = product.company
    data['price'] = product.price
    list_of_products.append(data)
    
  return list_of_products

