from project_files import app
from project_files import bcrypt

from .database import Users, UsersProducts, Products

from .scripts.functions import save_event

from flask import url_for, redirect

from datetime import datetime


@app.route('/create-user', methods=['GET', 'POST'])
def create_user():
    try:
        for user in range(3,5):
            add_user = Users(
                username=f'testuser{user}',
                first_name=f'user{user}',
                surname=f'user{user}',
                email=f'user@test{user}.pl',
                password=bcrypt.generate_password_hash(f'testuser{user}').decode('utf-8'),
                ip=f'127.0.0.1',
                account_type='admin',
                active=True,
                points=0,
                newsletter=False,
                date=f"{str(datetime.now().strftime('%d-%m-%Y  %H:%M:%S'))}",      
            )
            add_user.add_row_to_db()
            return redirect( url_for('login'))

    except Exception as e:
        save_event(event=e, site=create_user.__name__)
        return 'xd'
     


@app.route('/test', methods=['GET', 'POST'])
def test():
  # for i in Users().all_rows:
  #   print(i)
  user = Users.query.get(1)

  print(user.all_rows)
  product = Products.query.get(1)
  user_product = UsersProducts(user_id=user.id, product_id=product.id, price=5500)
  user_product.add_row_to_db()

  # user_product = UsersProducts.query.join(Products).join(Users).filter(Users.id == 1).all()
  # user_product = UsersProducts.query.join(Products).filter(user.id == 1).all()
  # user_product = Products.query.get(1)
  # user_product = user_product.user
  # for x in user_product:
  #   print(x.users.surname)
  #   print(x.price)
  return 'x'