from os import path
from flask import Blueprint
auth=Blueprint('auth',__name__)

def getcredspath():
    credspath=path.join(path.abspath(path.dirname(__package__)),'google-credentials.json')
    return credspath
from . import routes
