from project_files import db
from project_files import BLOCKED, USER, PRODUCT, EVENTS, DATA

from flask import request, abort, session
from flask_login import  current_user

from functools import wraps

from ..database import Blocked, User, Product

from datetime import datetime, date, timedelta

from collections import Counter

import json
import os
import string
import random



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


def not_null(field):
    if field != '' and field != None:
        return field

    else:
        raise ValueError      
 


def user_searched(username, ip, searched):

    objects_list = []

    with open(DATA) as fp:
        objects_list = json.load(fp)
        # for obj in objects_list:
        #     print(obj)

    searched = str(searched).lower()

    objects_list.append({
            "username": f"{username}",
            "ip": f"{ip}",
            "searched": f"{searched}"
        })

    with open(DATA, 'w') as json_file:
        json.dump(objects_list, json_file, indent=4, separators=(',', ': '))
    

def string_to_date(date):
  return datetime.strptime(date, '%d-%m-%Y  %H:%M:%S')


def unblock(blocked_user):

    if date.today() > string_to_date(blocked_user.date):
        try:
            db.session.delete(blocked_user)
            db.session.commit()
            save_error(error=f'{blocked_user} was unblocked', site='Login Page')
            return True

        except Exception as e:
            save_error(error=e, site='Login page')
            return False
    else:
        return False


def save_error(error, site):

    objects_list = []

    with open(EVENTS) as fp:
        objects_list = json.load(fp)

    durabity = string_to_date(str((datetime.now() - timedelta(days=7)).strftime("%d-%m-%Y")))

    current_errors = [object for object in objects_list if string_to_date(object['time'][0:10]) > durabity]

    current_errors.append({
            "error": f"{error}",
            "time": f"{str(datetime.now().strftime('%d-%m-%Y  %H:%M:%S'))}",
            "site": f"{site}"
        })

    elements = []
    for element in current_errors:
        if element not in elements:
            elements.append(element)

    with open(EVENTS, 'w') as json_file:
        json.dump(elements, json_file, indent=4, separators=(',', ': '))


def recently_searched():

    objects_list = []

    with open(DATA) as fp:
        objects_list = json.load(fp)

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
    
    url = ''
    for element in random_choices:
        url += element
    
    return url


def check_session(session_list):

    new_session = random_string(size=40)
    wheter_exists = False
    
    for sess in session_list:
        if sess['session'] == new_session:
            wheter_exists = True
            return check_session(session_list)
    
    if wheter_exists == False:
        return new_session 