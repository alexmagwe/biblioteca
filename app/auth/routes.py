# from .googleauth import Gauth
from  __future__ import print_function
from . import auth
import os
from google.auth.exceptions import RefreshError
from notes01.app import login_manager
from flask import render_template,url_for,redirect,abort,session,current_app,request,flash
from flask_login import current_user,login_user,logout_user,login_required,UserMixin
import requests,json
from oauthlib.oauth2 import WebApplicationClient
from notes01.app.models import Users,AdminsList
from .forms import AdminForm
import pickle
from .authflow import authflow
client=WebApplicationClient(os.environ.get('GOOGLE_CLIENT_ID'))
import os.path
from google.auth.transport.requests import Request

def get_google_config():
    return  requests.get(current_app.config['GOOGLE_DISCOVERY_URL']).json()

@auth.route('/home')
@auth.route('/')
def home():
    if current_user.is_authenticated:
        return render_template('home.html')
    else:
        print('user not logged in')
        return render_template('landing.html')
@auth.route('/')
def student():
    return render_template('home.html')

@auth.route('/login',methods=['POST','GET'])
def login():
    googleprovider=get_google_config()
    auth_endpoint=googleprovider['authorization_endpoint']
    request_uri=client.prepare_request_uri(auth_endpoint,redirect_uri=request.base_url+'/callback',scope=['openid','email','profile'])
    return redirect(request_uri)

@auth.route('/login/callback')
def callback():
    googleprovider=get_google_config()
    user_data=authflow(googleprovider,client)
    user=Users.query.filter_by(email=user_data['email']).first()
  
    if user.is_admin:
        login_user(user)
    else:
        abort(403,'You are not an admin')
    return redirect(url_for('auth.home'))
  


@login_required
@auth.route('/add_admin',methods=['GET','POST'])
def add_admin():
    form=AdminForm()
    if not current_user.is_admin:
        abort(403)
    if form.validate_on_submit():
        admin=AdminsList(email=form.email.data)
        res=admin.add()
        flash(res,'success')
    return render_template('auth/add_admin.html',form=form)
@login_required
@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.home'))
