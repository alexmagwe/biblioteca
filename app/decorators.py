from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permissions,Users
from .errorHandler import sendError, sendSuccess, sendWarning


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_func(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_func
    return decorator
def admin_required(f):
    return permission_required(Permissions.Admin)(f)

    
            
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
            token=token.split(" ")[1]

        if not token:
            return {'message': 'a valid token is missing'}
        try:
            data = decode_auth_token(token)
            curr_user = Users.query.filter_by(email=data['email']).first().to_json()
            request.user=curr_user
        except jwt.ExpiredSignatureError:
            return sendError('Signature expired. Please log in again.')
        except jwt.InvalidTokenError:
            return sendError('Invalid token. Please log in again.')
        return f(*args, **kwargs)
    return decorator            
