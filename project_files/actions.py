from project_files import db
from .database import User, Blocked


def delete_rows(model, data):
    for number in data:
        print(number)
        model.query.filter_by(id=number).delete()
        db.session.commit()