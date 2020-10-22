from flask import url_for,render_template,current_app
from flask_login import current_user
from . import main


@main.route('/home')
@main.route('/')
def home():
    if current_user.is_authenticated:
        print('user is authenticated')
        return render_template('landing.html')
    else:
        return render_template('home.html')

                           
@main.route('/new_course',methods=['GET'])
def new_course():
    return render_template('addcourse.html')


@main.route('/find_notes',methods=['GET'])
def find_notes():
    return render_template('notes.html')

@main.route('/courses',methods=['GET'])
def courses():
    return render_template('data/courses.html')

@main.route('/units',methods=['GET'])
def units():
    return render_template('data/units.html')

@main.route('/notes',methods=['GET'])
def notes():
    return render_template('data/notes.html')

@main.route('/users',methods=['GET'])
def users():
    return render_template('data/users.html')



@main.route('/upload_notes',methods=['GET'])
def upload_notes():
    return render_template('upload.html')

@main.route('/docs',methods=['GET'])
def docs():
    return render_template('/docs/doc.html')
