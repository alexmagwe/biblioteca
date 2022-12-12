from flask import url_for,render_template,current_app
from flask_login import current_user
from . import myapi,api


@api.route('/home')
@api.route('/')
def home():
    if current_user.is_authenticated:
        return render_template('landing.html')
    else:
        return render_template('home.html')

                           
@api.route('/new_course',methods=['GET'])
def new_course():
    return render_template('addcourse.html')


@api.route('/find_notes',methods=['GET'])
def find_notes():
    return render_template('notes.html')
    
@api.route('/docs',methods=['GET'])
def docs():
    return render_template('/docs/doc.html')