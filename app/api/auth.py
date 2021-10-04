import jwt 
from . import myapi
import datetime
from flask import request,jsonify
from .. import db
from sqlalchemy import exc
from .resources import find_user
from flask_restx import Resource, reqparse, fields
from ..models import Users, Notes, Categories, RoleReviewList, Permissions
# signup_model=myapi.model('SignUp',{'email':fields.String,'password':fields.String})
from ..errorHandler import sendError, sendSuccess, sendWarning
import os
from ..auth import decode_auth_token,create_auth_token

signup_model=myapi.model('SignUp',{'email':fields.String,'password':fields.String,'username':fields.String})
signin_model=myapi.model('Login',{'email':fields.String,'password':fields.String})

class SignUp(Resource):
    @myapi.expect(signup_model)
    def post(self):
        data=request.json
        email=data.get('email')
        password=data.get('password')
        username=data.get('username')
        if email and password and username:
            user=Users(email=email ,username=username)
            user.set_password(password)
        elif email and username and not password:
            user=Users(email=email,username=username)
        db.session.add(user)
        try:
            db.session.commit()
            if (token:=create_auth_token(user.to_json())):
                return jsonify(data=token,type="success",status=201,message="Signup successful")
        except exc.IntegrityError as e:
            return sendError('User with the email provided already exists')
        
            

class Login(Resource):
    @myapi.expect(signin_model)
    def post(self):
        data=request.json
        if data:
            email=data.get('email')
            password=data.get('password')
            if email:
                user=find_user(email)
                if not user:
                    return sendError('User not found, Please create an account.')
                else:    
                    if password:
                        if user.verify_password(password):
                            #if(token:=create_auth_token(user.to_json())):
                             #   return jsonify(data=token,type="success",status=201,message="Signin successful")
                            return user.to_json()
                        else:
                            return sendError('Invalid Email/Password')
        else:
            return sendError('Missing Information'),400


        
    
