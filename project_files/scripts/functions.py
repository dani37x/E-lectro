from project_files import db
from project_files import app
from project_files import queue
from project_files import BLOCKED, USER, PRODUCT
from project_files import EVENTS, DATA, CLASSIFIER
from project_files import SESSIONS, PRICES

from ..database import Blocked, User, Product

from flask import request, abort, session, redirect, url_for
from flask_login import  current_user

from functools import wraps

from datetime import datetime, date, timedelta

from collections import Counter

from rq import Retry

import json
import string
import random
import pickle


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

            check = Blocked.query.filter_by(ip=request.remote_addr).first()
            if check != None:
                abort(403)

            check = Blocked.query.filter_by(username=current_user.username).first()
            if check != None:
                abort(403)

            check = User.query.filter_by(username=current_user.username).first()
            if check.active == False:
                abort(403)

            return f(*args, **kwargs)
        return wrapped
    return decorator


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


def not_null(field):
    if field != '' and field != None:
        return field
    else:
        return ValueError    
 

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
    

def string_to_date(date):
  return datetime.strptime(date, '%d-%m-%Y  %H:%M:%S')


def unblock(blocked_user):
    app.app_context().push()

    if (datetime.now() > string_to_date(blocked_user.date)):
        try:
            db.session.delete(blocked_user)
            db.session.commit()
            save_event(event=f'{blocked_user} was unblocked', site='Login Page')
            return True

        except Exception as e:
            save_event(event=e, site='Login page')
            return False
    else:
        return False


def save_event(event, site):
    file_path = back_to_slash(EVENTS)
    objects_list = open_json(file_path=file_path)

    objects_list.append({
            "event": f"{event}",
            "time": f"{str(datetime.now().strftime('%d-%m-%Y  %H:%M:%S'))}",
            "site": f"{site}"
        })

    save_json(file_path=EVENTS, data=objects_list)


def recently_searched():

    objects_list = open_json(file_path=DATA)
    # if len(objects_list) > 0:

    queries = [object['searched'] for object in objects_list if len(object['searched']) > 2]
    counter = Counter(queries)

    return dict(counter.most_common()[:5])

    
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


def check_session(session_list):
    new_session = random_string(size=40)
    wheter_exists = False
    
    for sess in session_list:
        if sess['session'] == new_session:
            wheter_exists = True
            return check_session(session_list)
    
    if wheter_exists == False:
        return new_session 


def delete_expired_data(d, h, m, file_path):
    objects_list = open_json(file_path=file_path)

    if len(objects_list) > 0:
        durabity = datetime.now() - timedelta(days=d, hours=h, minutes=m)
        current_objects = [object for object in objects_list if string_to_date(object['time']) > durabity]

        save_json(file_path=file_path, data=current_objects)


def similar_products_to_queries(username):
    queries = open_json(file_path=DATA)
    user_queries = [query for query in queries if query['username'] == username]
   
    if products := Product.query.all():
        
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


def failed_captcha(username):
    object_list = open_json(file_path=EVENTS)
    sentence = f'The user {username}'    
    counter = 0

    for object in object_list:
        if object['site'] == 'captcha' and sentence in object['event']:
            counter += 1
            
        if counter == 4:
            return True
        
    return False


def save_price(data):
    file_path = back_to_slash(PRICES)
    objects_list = open_json(file_path=file_path)

    for object in data:
        print(object, type(object))
        objects_list.append({
                "id": f"{object.id}",
                "name": f"{object.name}",
                "price": f"{object.price}",
                "time": f"{str(datetime.now().strftime('%d-%m-%Y  %H:%M:%S'))}",
            })
        
    save_json(file_path=file_path, data=objects_list)


def the_lowest_price(product):
    objects_list = open_json(file_path=PRICES)
    product_info = []

    for object in objects_list:
        if int(object['id']) == product.id:
            product_info.append(float(object['price']))

    return min(product_info)
