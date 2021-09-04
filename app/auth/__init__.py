from os import path
from flask import Blueprint,current_app,request,jsonify
import datetime,jwt
auth=Blueprint('auth',__name__)

def getcredspath():
    credspath=path.join(path.abspath(path.dirname(__package__)),'google-credentials.json')
    return credspath
from . import routes
from flask import current_app,request,jsonify
import datetime,jwt

def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: dict|error
    """
    try:
        payload = jwt.decode(auth_token, current_app.config['SECRET_KEY'],algorithms='HS256')
        return payload['sub']
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError
        # return sendError('Signature expired. Please log in again.')
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError
def create_auth_token(user_data):
    """
    Encodes the user data
    :param user_data
    :return token|string
    """
    try:
        payload={'sub':user_data,'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=30),'iat':datetime.datetime.utcnow()}
        return jwt.encode(payload, current_app.config['SECRET_KEY'])
    except Exception as e:
        print(e)
        return False 
