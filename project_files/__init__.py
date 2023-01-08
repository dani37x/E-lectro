from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from flask_mail import Mail, Message

import os


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'
app.secret_key = 'hello'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["30 per hour", "10 per minute", "100 per day"],
    storage_uri="memory://",
)


mail = Mail(app)

app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'not set')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'not set')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False