from flask import Flask, session

from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from flask_mail import Mail, Message

from flask_bcrypt import Bcrypt

from apscheduler.schedulers.background import BackgroundScheduler

import redis
from rq import Queue
from rq.registry import FailedJobRegistry

import os


disallowed_words = [
  'fuck', 'shit', 'hitler', 'stalin', '666', 
  'admin', 'mod', 'product', 'blocked', 'user',
  'the user', 'captcha'
]


# main config


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static'
app.secret_key = 'hello'

DATE_FORMAT = '%d-%m-%Y'
DATETIME_FORMAT = ''
FLASK_ENV = 'env'
SERVER_NAME = ''


#  files' paths


BLOCKED = r'D:\projekty\E-lectro\instance\BLOCKED.json'
PRODUCT = r'D:\projekty\E-lectro\instance\PRODUCT.json'
USER = r'D:\projekty\E-lectro\instance\USER.json'
CLASSIFIER = r'D:\projekty\E-lectro\project_files\machine_learning\classifier.pkl'
EVENTS = r'D:.\instance\EVENTS.json'
DATA = r'.\instance\DATA.json'
SESSIONS = r'.\instance\SESSIONS.json'
PRICES = r'.\instance\PRICES.json'


# database and login


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


# limiter


limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["450 per hour", "100 per minute", "1000 per day"],
    storage_uri="memory://",
)

# mail


mail = Mail(app)

app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'not set')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'not set')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False



# session duration

# set on when server would start

# session.permanent = True
# app.permanent_session_lifetime = timedelta(hours=24)


# Flask bcrypt


bcrypt = Bcrypt(app)


# redis


redis_instance = redis.Redis(
    host='127.0.0.1',
    port=6379
    )

queue = Queue(connection=redis_instance)

job_registry = FailedJobRegistry(queue=queue)


# scheduler


scheduler = BackgroundScheduler(timezone="Europe/Warsaw")