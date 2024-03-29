"""
The file errors.py contains error handlers for the entire application
and addresses the most common errors. These error handlers collect the
errors and store them in a file called EVENTS.json, which works in
conjunction with the event system. 

This approach can help to streamline the error handling process and 
ensure that issues are properly recorded for future reference.
"""


from project_files import app

from .scripts.functions import save_event


@app.errorhandler(405)
def handle_405(e):
    save_event(event=e, site=handle_404.__name__)
    return '405'


@app.errorhandler(404)
def handle_404(e):
    return '404'


@app.errorhandler(403)
def handle_403(e):
    save_event(event=e, site=handle_403.__name__)
    return '403'


@app.errorhandler(401)
def handle_401(e):
    save_event(event=e, site=handle_401.__name__)
    return '401'


@app.errorhandler(400)
def handle_400(e):
    save_event(event=e, site=handle_400.__name__)
    return '400'


@app.errorhandler(503)
def handle_503(e):
    save_event(event=e, site=handle_503.__name__)
    return '503'


@app.errorhandler(500)
def handle_500(e):
    save_event(event=e, site=handle_500.__name__)
    return '405'
