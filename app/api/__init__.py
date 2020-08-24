from flask import Blueprint
from flask_restx import Api
api=Blueprint('api',__name__)
myapi=Api(api)
from . import routes2
