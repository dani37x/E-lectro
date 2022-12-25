from project_files import db
from .database import User, Blocked


def delete_rows(model, data):
    for number in data:
        model.query.filter_by(id=number).delete()
        db.session.commit()

def block_user(data):
    for user in data:
        user_to_block = User.query.get(id=user)
        new_row = Blocked(
            username=user_to_block.username,
            ip='127.0.0.1'
        )
        db.session.add( new_row)
        db.session.commit()