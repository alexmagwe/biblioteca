from flask import url_for,render_template,current_app
from flask_login import current_user
from . import main


@main.route('/home')
@main.route('/')
def home():
    if current_user.is_authenticated:
        return render_template('landing.html')
    else:
        return render_template('home.html')

                           
@main.route('/new_course',methods=['GET'])
def new_course():
    return render_template('addcourse.html')


@main.route('/find_notes',methods=['GET'])
def find_notes():
    return render_template('notes.html')
    

@main.route('/upload_notes',methods=['GET'])
def upload_notes():
    return render_template('upload.html')

@main.route('/docs',methods=['GET'])
def docs():
    return render_template('/docs/doc.html')
