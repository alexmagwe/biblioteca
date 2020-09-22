from flask import Blueprint
from flask_restx import Api
api=Blueprint('api',__name__)
myapi=Api(api,doc='/docs/',title='Biblioteca api',description='University notes api,Try it out below')
from . import routes,routes2
