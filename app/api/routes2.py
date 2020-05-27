from flask import Flask,jsonify,request,url_for,render_template
import requests
from notes.app import login_manager,db
from . import api
import requests
import os,json
from ..models4 import Courses,Units,Users,Notes

def find_user(em):
    user=Users.query.filter_by(email=em).first()
    return user
def find_course(name):
    course=Courses.query.filter_by(name=name).first()
    return course

@api.route('/get_courses',methods=['GET'])
def get_courses():
    courses=Courses.query.all()
    data=[course.name for course in courses]
    return jsonify({"courses":data})    

@api.route('/all_notes')
def all_notes():
    notes=Notes.query.all()
    data=[[note.name,note.path] for note in notes]
    return jsonify({"notes":data})    

@api.route('/user_details',methods=['GET','POST'])#data ={email:useremail}
def userdetails():
    data=request.json
    print(data  )
    em=data.get('email')
    print(type(em))
    
    if not em:
        return jsonify({'error':'no email provided'}),404 
    print(em)
    # email=data.get('email')
    user=find_user(em)
    if user and user.course:
        course_name=user.course.name
        return jsonify({'course':course_name})

    elif not user:
        user=Users(email=em)
        db.session.add(user)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        return jsonify({'course':''})   
    else:
        return jsonify({'course':""})

@api.route('/add_mycourse',methods=['POST'])
def add_mycourse():
    data=request.json
    if data.get('email') and data.get('course_name'):
        user=find_user(data['email'])
        course_name=data.get('course_name')
        if user:
            email=user.email
        else: 
            return jsonify({'error':'user not found'})
        course=find_course(course_name)
        
        if user and course and not user.course:
            user.course_id=course.id
            db.session.commit()
            return jsonify({'course_name':user.course.name})            
        elif user.course:
            return jsonify({'message':'course details already available'})
    else:
        return jsonify({'error':'missing information'})
            

    
@api.route('/get_course_notes',methods=['GET'])
def course_notes():
    data=request.json#recieve json inform of {'course_name':'name}
    if data and data.get('course_name' is not None):
        course_name=data['course_name']
        notes=get_notes(course_name)
        if notes:
            return notes
        else:
            return jsonify({'error':'no notes found'})
            #send_ notes request email implementation
    else:
        return jsonify({'error':'course name needed'})
def get_notes(course_name):
    course=find_course(course_name)
    part1=course.name
    part2=course.units
    print(part2)
    part3=[{y.year:[{u.semester:[{unit.acronym:[{'url':note.path} for note in unit.notes]} for unit in  part2]} for u in part2]}for y in part2]
    
    # structureit(notes)
    return jsonify({part1:part3})

@api.route('/add_notes',methods=['GET'])
def add_notes():
    return render_template('upload.html')
            
            
@api.route('/upload',methods=['POST'])            
def upload():
    if 'files' not in request.files:
        return jsonify({'error',' no file was chosen'})
    acronym=request.form.get('unit_prefix')
    print('\n\nacroynm',acronym)
    for file in request.files.getlist('files'):
        print(file.filename)
        savefile(file,acronym)
    return jsonify({'info':'request complete'})
        
@api.route('/get_units',methods=['GET'])
def get_units():
     units=Units.query.all()
     unit_names=[[{'acronym':unit.acronym,'name':unit.name,'year':unit.year,'semester':unit.semester}] for unit in units]
     return jsonify({'units':unit_names})

def savefile(file,unit_prefix):
    _id,path=find_unit(unit_prefix)
    if path:
        file_url=os.path.join(path,file.filename)
        try:
            file.save(file_url)
            notes=Notes(name=file.filename,path=file_url,unit_id=_id)
            db.session.add(notes)
            try:
                db.session.commit()
            except:
                db.session.rollback()
        except:
           return jsonify({'error':'upload failed'})
            
    else: 
        return ({'error':'path not found'}),404
        #create_new_path(unit)

def find_unit(unit_prefix):
        unit=Units.query.filter_by(acronym=unit_prefix).first()
        if unit:
            return (unit.id,unit.path)
        else:
            return (None,None)     
@api.route('/create_course',methods=['GET','POST'])
def create_course():
    if request.method=='POST':
        data=request.json
        if data.get('course_name'):
            name=data.get('course_name')
            course=find_course(name)
            if course:
                return jsonify({'error':'course already exists'})
            else:
                c=Courses(name)
                db.session.add(c)
                try:
                    db.session.commit()
                    return jsonify({'success':"course added"})
                except:
                    db.session.rollback()
    
            