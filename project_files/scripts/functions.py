"""
The functions.py file in the E-lectro project serves as a collection of general-purpose
functions and utilities.

The file contains various functions that are used to support different features of
the project, such as handling JSON files, generating random characters and strings,
providing security wrappers for authentication and permission checks, implementing
a search ranking system, and providing a captcha system to verify user input.

Overall, the functions.py file is an important component of the E-lectro project,
providing a collection of utility functions that help to make the project more robust,
secure, and functional.
"""

from project_files import db
from project_files import app
from project_files import EVENTS, DATA, CLASSIFIER, PRICES
from project_files import disallowed_words

from ..database import BlockedUsers, Users, Products

from flask import request, abort, session, redirect, url_for
from flask_login import  current_user

from functools import wraps

from datetime import datetime, date, timedelta

from collections import Counter

import json
import string
import random
import pickle


# funtions for files


def open_json(file_path):
    data = []
    with open(file_path) as fp:
        data = json.load(fp)
    return data


def save_json(file_path, data):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4, separators=(',', ': '))


def back_to_slash(path):
  return path.replace(r" \ ".strip(), '/')


def save_event(event, site):
    file_path = back_to_slash(EVENTS)
    objects_list = open_json(file_path=file_path)

    objects_list.append({
            "event": f"{event}",
            "time": f"{str(datetime.now().strftime('%d-%m-%Y  %H:%M:%S'))}",
            "site": f"{site}"
        })

    save_json(file_path=EVENTS, data=objects_list)


def delete_expired_data(d, h, m, file_path):
    objects_list = open_json(file_path=file_path)

    if len(objects_list) > 0:
        durabity = datetime.now() - timedelta(days=d, hours=h, minutes=m)
        current_objects = [obj for obj in objects_list if string_to_date(obj['time']) > durabity]
        save_json(file_path=file_path, data=current_objects)


# string functions


def string_to_date(date):
  return datetime.strptime(date, '%d-%m-%Y  %H:%M:%S')


def random_char(disabled_char=None, without=None):
  list_of_chars = []
  list_of_chars.extend(string.ascii_lowercase)
  list_of_chars.extend(string.ascii_uppercase)
  list_of_chars.extend(string.digits)
  list_of_chars.extend(string.punctuation)

  if disabled_char != None:
    list_of_chars.remove(disabled_char)

  if without != None:
    for ch in without:
      list_of_chars.remove(ch)

  return random.choice(list_of_chars)


def random_string(size):
    small = string.ascii_lowercase
    big = string.ascii_uppercase
    numbers = string.digits
    s =  small + big  + numbers
    
    random_choices = random.sample(s, size)
    random.shuffle(random_choices)
    string_to_return = ''

    for element in random_choices:
        string_to_return += element
    
    return string_to_return


# database functions


def rq_add_row_to_db(obj):
    app.app_context().push()
    db.session.add(obj)
    db.session.commit()


def rq_delete_db_row(obj):
    app.app_context().push()
    db.session.delete(obj)
    db.session.commit()


# protection wrappers


def check_admin(name):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):

            if current_user.username != 'Admin' or current_user.username != 'admin':
                abort(403)    

            return f(*args, **kwargs)
        return wrapped
    return decorator


def check_user(name):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):

            check = BlockedUsers.query.filter_by(ip=request.remote_addr).first()
            if check != None:
                abort(403)

            check = BlockedUsers.query.filter_by(username=current_user.username).first()
            if check != None:
                abort(403)

            check = Users.query.filter_by(username=current_user.username).first()
            if check.active == False:
                abort(403)

            return f(*args, **kwargs)
        return wrapped
    return decorator


# the captcha wrapper and the captcha system


def captcha(name):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            
            session['previous_site'] = name
            if session.get('captcha_completed', None) == None:
                return redirect( url_for('captcha'))

            return f(*args, **kwargs)
        return wrapped
    return decorator


def failed_captcha(username):
    object_list = open_json(file_path=EVENTS)
    sentence = f'The user {username}'    
    counter = 0

    for obj in object_list:
        if obj['site'] == 'captcha' and sentence in obj['event']:
            counter += 1
        if counter == 4:
            return True
    
    return False
    

def generator(answer, obstacle):
    chars = [answer, obstacle]
    list_of_numbers = [2, 5, 4, 6, 7, 8, 9, 10, 11, 12, 15, 16]
    size = random.choice(list_of_numbers)
    list_of_chars = []
    data = {
      'answer_count': 0, 
      'obstacle_count': 0, 
      'generated_string': ''
    }

    for j in range(0, (size*size)):
        if data['answer_count'] < random.choice(list_of_numbers):
            char_to_add = random.choice(chars)
        else:
            char_to_add = obstacle

        list_of_chars.append(char_to_add)
        
        if char_to_add == answer:
            data['answer_count'] += 1
        else:
            data['obstacle_count'] += 1

    random.shuffle(list_of_chars)
    element_count = 0

    for element in list_of_chars:
        if element_count % size == 0:
            data['generated_string'] += '\n'
            
        data['generated_string'] += element
        element_count += 1

    return data


# the unblocker function after expired time-block


def unblock():
    app.app_context().push()
    blocked_users = BlockedUsers().all_rows

    for blocked in blocked_users:
        if (datetime.now() > string_to_date(blocked.date)):
            try:
                db.session.delete(blocked)
                db.session.commit()
                save_event(event=f'{blocked.username} was unblocked', site='unblocker')

            except Exception as e:
                save_event(event=e, site='unblocker')


# Trending rank built from user queries


def user_searched(username, ip, searched):
    objects_list = open_json(file_path=DATA)
    searched = str(searched).lower()

    objects_list.append({
            "username": f"{username}",
            "ip": f"{ip}",
            "searched": f"{searched}",
            "time": f"{str(datetime.now().strftime('%d-%m-%Y  %H:%M:%S'))}"
        })

    save_json(file_path=DATA, data=objects_list)


def recently_searched():
    objects_list = open_json(file_path=DATA)
    queries = []

    if len(objects_list) > 0:
        for obj in objects_list:
            if len(obj['searched']) > 2 and obj['searched'] not in disallowed_words:
                queries.append(obj['searched'])

        counter = Counter(queries)
        return dict(counter.most_common()[:5])


def similar_products_to_queries(username):
    queries = open_json(file_path=DATA)
    user_queries = [query for query in queries if query['username'] == username]
   
    if products := Products().all_rows:
        
        if len(user_queries) == 0:
            random_products = []
            for number in range(6):
                product_to_add = random.choice(products)
                if product_to_add not in random_products:
                    random_products.append(product_to_add)

            return random_products

        possible_products = []
        for product in products:
            for query in user_queries:
                # print(query['searched'], product.name)
                # print(type(query['searched']), type(product.name))
                if str(query['searched']).lower() in str(product.name).lower() or query['searched'] == product.name:
                    if product not in possible_products:
                        possible_products.append(product)

                if str(query['searched']).lower() in str(product.category).lower() or query['searched'] == product.name:
                    if product not in possible_products:
                        possible_products.append(product)

        return possible_products[0:7]


# session checker


def check_session(session_list):
    new_session = random_string(size=40)
    wheter_exists = False
    
    for sess in session_list:
        if sess['session'] == new_session:
            wheter_exists = True
            return check_session(session_list)
    
    if wheter_exists == False:
        return new_session 


# ML Classifier implement (more in ML directory)


def classification(category, money):
    #more to add
    list_of_categories = [
        {"AGD": 1},
        {"TOYS": 2},
    ]
    for cat in list_of_categories:
        if category in cat:
            category = cat[category]

    model = pickle.load(open(CLASSIFIER, "rb"))
    prediction = model.predict([[category, money]])
    
    return prediction


# pricing system


def save_price(product, days=0):
    file_path = back_to_slash(PRICES)
    objects_list = open_json(file_path=file_path)
    days = int(days) if days != '' else 0

    objects_list.append({
            "id": f"{product.id}",
            "name": f"{product.name}",
            "price": f"{product.price}",
            "old_price": f"{product.old_price}",
            "start_date": f"{datetime.now().strftime('%d-%m-%Y  %H:%M:%S')}",
            "end_date": f"{(datetime.now() + timedelta(days=days)).strftime('%d-%m-%Y  %H:%M:%S')}"
        })
    
    save_json(file_path=file_path, data=objects_list)


def the_price(product, price_type):
    objects_list = open_json(file_path=PRICES)
    product_info = []

    for obj in objects_list:
        if int(obj['id']) == product.id:
            product_info.append(float(obj['price']))
            product_info.append(float(obj['old_price']))

    if price_type == 'the_lowest_price':
        return min(product_info)
    elif price_type == 'the_highest_price':
        return max(product_info)


def end_of_promo():
    app.app_context().push()
    object_list = open_json(file_path=PRICES)
    not_ended = []
    
    if len(object_list) > 1:
        for obj in object_list:
            if string_to_date(obj['end_date']) < datetime.now() \
                and obj['start_date'] != obj['end_date']:

                product = Products.query.get(int(obj['id']))
                
                if float(obj['price']) == product.price: 
                    variable = product.price
                    product.price = product.old_price
                    product.old_price = variable
                    db.session.commit()

            else:
                not_ended.append(obj)
            
        save_json(file_path=PRICES, data=not_ended)