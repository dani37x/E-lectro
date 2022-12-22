from flask import request, abort

from .database import Blocked

def checker(username):
    check = Blocked.query.filter_by(ip=request.remote_addr).first()
    if check != None:
        abort(404, description='You are banned')
    check = Blocked.query.filter_by(username=username).first()
    if check != None:
        abort(404, description='You are banned')
