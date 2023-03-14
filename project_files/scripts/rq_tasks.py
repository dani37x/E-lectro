from project_files import app
from project_files import db



def rq_add_row_to_db(object):
    
    app.app_context().push()
    db.session.add(object)
    db.session.commit()


def rq_delete_db_row(object):

    app.app_context().push()
    db.session.delete(object)
    db.session.commit()


