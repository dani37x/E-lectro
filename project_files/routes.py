from project_files import app
from project_files import db

from flask import Flask, render_template, url_for, redirect, flash
# from flask_login import LoginManager

from .form import UserCreate

from .database import User


@app.before_first_request
def before_first_request():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def page():
  return render_template('page.html')

@app.route('/accounts/register/', methods=['GET', 'POST'])
def accounts_register():
  form = UserCreate()
  # if form.validate_on_submit():
    
  return render_template('login.html')


@app.errorhandler(404)
def handle_404(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def handle_500(e):
    return render_template('500.html'), 500