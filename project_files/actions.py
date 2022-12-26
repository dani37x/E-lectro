from project_files import db
from .database import User, Blocked


def delete_rows(model, data):
    for number in data:
        model.query.filter_by(id=number).delete()
        db.session.commit()

def block_user(data):
    for user in data:
        user_to_block = User.query.get(id=user)
        user_to_block.active = False
        
        new_row = Blocked(
            username=user_to_block.username,
            ip=user_to_block.ip
        )
        db.session.add(new_row)
        db.session.commit()