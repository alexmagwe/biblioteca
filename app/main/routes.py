from flask import url_for,render_template,current_app,redirect,request,flash
from flask_login import current_user
from ..models import Units,Notes
from ..filters import filter_extension,filter_semester,filter_year,filter_year_and_semester
from . import main
from ..errorHandler import showError
import os
from ..auth.drivemanager import Gdrive

gdrive=Gdrive()
@main.route('/home')
@main.route('/')
def home():
    if current_user.is_authenticated:
        units=Units.query.order_by("code").all()
        return render_template('landing.html',units=units)
    else:
        return render_template('home.html')
@main.route('/drive/page/<int:page>',methods=[ 'GET','POST'])
def drive(page):
    if len(gdrive.files)>0 and page<=len(gdrive.files):
        files=gdrive.files[page]
    else:
        gdrive.get_files(30)
        files=gdrive.files
        files=files[page]
    storage=gdrive.calculate_storage()
    pages=len(gdrive.files)
    num_files=gdrive.get_num_files()
    return render_template('drive/drive.html',files=files,num=num_files,storage=storage,pages=pages)

@main.route('/reload_drive/',methods=[ 'GET'])
def reload_drive():
    gdrive.files=[]
    return redirect(url_for('main.drive',page=1))

@main.route('/duplicates',methods=[ 'GET','POST','DELETE'])
def duplicates():
    if len(gdrive.files)==0:
        gdrive.get_files(30)
    if len(gdrive.duplicateslist)==0:
        duplicates=gdrive.find_duplicates()
    else:
        duplicates=gdrive.duplicateslist
    num=len(duplicates)
    if request.method=='DELETE':
        # failed=gdrive.test_delete_duplicates()
        res=gdrive.delete_duplicates()
        if res:
            return {'error':f'{res}'}
        else:return {'success':f'{num} duplicate files deleted succesfully'}
    return render_template('drive/duplicates.html',duplicates=duplicates,num=num)

# @main.route('/duplicates',methods=['DELETE'])
# def deleteduplicates():
    
    
                           
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
@main.route('/delete/<gid>',methods=['GET'])
def delete(gid):
    res=gdrive.delete_file(gid)
    if res.get('success'):
        res=Notes.query.filter_by(gid=gid).first().delete_file()
        if res:
            flash('succesfully deleted','success')
        else:
            flash('internal server error occured try again later','error')
            # return {'message':"failed to delete internal server error occured,try again later"}
    else:
        flash(str(res))
    return redirect(url_for('main.units'))
    
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

@main.route("/search",methods=['POST'])
def search():
    query=request.get_json().get("query")

    if not query:
        return showError("Empty query")
    results=gdrive.search(query)
    return results

@main.route('/upload_notes',methods=['GET'])
def upload_notes():
    return render_template('upload.html')

@main.route('/docs',methods=['GET'])
def docs():
    return render_template('/docs/doc.html')

