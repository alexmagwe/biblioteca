from flask import url_for,render_template,current_app,redirect,request
from flask_login import current_user
from ..models import Units,Notes
from ..filters import filter_extension,filter_semester,filter_year,filter_year_and_semester
from . import main
import os


@main.route('/home')
@main.route('/')
def home():
    if current_user.is_authenticated:
        units=Units.query.order_by("code").all()
        return render_template('landing.html',units=units)
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
    units=Units.query.all()
    return render_template('data/units.html',units=units)

@main.route('/notes',methods=['GET'])
def notes():
    notes=Notes.query.all()
    return render_template('data/notes.html',notes=notes)

@main.route('/users',methods=['GET'])
def users():
    return render_template('data/users.html')

@main.route('/units/<int:id>',methods=['GET'])
def unit(id):
    unit=Units.query.get(id)
    return render_template('unit/unit.html',unit=unit,notes=unit.notes)

@main.route('/filter/units/',methods=['GET'])
def filter_units():
    year,semester=request.args.get('year'),request.args.get('semester')
    if year and semester:
        year=int(year)
        results=filter_year_and_semester(year,semester)
        return render_template('data/units.html',units=results)
    elif year and not semester:
        results=filter_year(year)
        return render_template('data/units.html',units=results)
    elif semester and not year:
        results=filter_semester(semester)
        return render_template('data/units.html',units=results)

    results=[]
    if case and unit:
        if case=='all':
            return render_template('unit/unit.html',unit=unit,notes=unit.notes)
        ext='.'+case
        results=filter_extension(unit.notes,ext)
    return render_template('unit/unit.html',unit=unit,notes=results)

#filtering notes of a single unit
@main.route('/filter/ext/<int:id>/',methods=['GET'])
def filter_ext(id):
    unit=Units.query.get(id)
    case=request.args.get('extension')
    results=[]
    if case and unit:
        if case=='all':
            return render_template('unit/unit.html',unit=unit,notes=unit.notes)
        ext='.'+case
        results=filter_extension(unit.notes,ext)
    return render_template('unit/unit.html',unit=unit,notes=results)
#filtering all notes
@main.route('/filter/ext/',methods=['GET'])
def filter_notes_ext():
    notes=Notes.query.all()
    case=request.args.get('extension')
    results=[]
    if case and unit:
        if case=='all':
            return render_template('data/notes.html',notes=notes)
        ext='.'+case
        results=filter_extension(notes,ext)
    return render_template('data/notes.html',notes=results)


@main.route('/upload_notes',methods=['GET'])
def upload_notes():
    return render_template('upload.html')

@main.route('/docs',methods=['GET'])
def docs():
    return render_template('/docs/doc.html')

