from flask import Flask,jsonify,request,url_for,render_template,session
import requests
from notes01.app import login_manager,db
from . import api
import requests
import os,json
from ..models4 import Courses,Units,Users,Notes
#helper functions
def find_user(em):
    user=Users.query.filter_by(email=em).first()
    return user
def find_course(name):
    course=Courses.query.filter_by(name=name).first()
    return course

def find_unit(unit_prefix):
        unit=Units.query.filter_by(acronym=unit_prefix).first()
        if unit:
            return (unit.id,unit.path)
        else:
            return (None,None)     
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
        return None
        #create_new_path(unit)
def get_notes(course_name):
    course=find_course(course_name)
    notes=[]
    if course:
        units=course.units
        for unit in units:
            for n in unit.notes:
                url=n.path.split('/')
                path="/".join(url[url.index('static'):])#conversion of absolute path to relative path
                print('path',path)
                notes.append({'unit':unit.acronym,'name':n.name,'url':path})
        if len(notes)>0:
            return jsonify({course_name:notes})
    else:
        return None
    return None#runs only if the notes list is zero


#routes
@api.route('/get_courses',methods=['GET'])
def get_courses():
    courses=Courses.query.all()
    data=[course.name for course in courses]
    return jsonify({"courses":data})    

@api.route('/all_notes')
def all_notes():
    notes=Notes.query.all()
    data=[{'name':note.name,"url":"/".join(note.path.split('/')[-8:]),'unit':note.unit.name} for note in notes]
    return jsonify({"notes":data})    

@api.route('/user_details',methods=['GET'])#data ={email:useremail}
def userdetails():
    data=request.args.get('email')
    print(data  )
    em=data.get('email')    
    if not em:
        return jsonify({'error':'no email provided'}),404 
    # email=data.get('email')
    user=find_user(em)
    if user and user.course:
        course_name=user.course.name
        session['user']=user
        return jsonify({'course':course_name})


    elif not user:
        user=Users(email=em)
        db.session.add(user)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            return jsonify({'error':'user could not be created'})
        session['user']=user
        return jsonify({'course':''})
 #if the user course is not set or for some reason its not found empty string will be returned          
    else:
        return jsonify({'course':""})

@api.route('/add_mycourse',methods=['POST'])
def add_mycourse():
    data=request.json
    if data.get('email') and data.get('course_name'):
        # user=find_user(data['email'])
        user=session.get('user')
        print('user',user)
        course_name=data.get('course_name')
        if user:
            email=user.email
        else: 
            return jsonify({'error':'user not found'})
        course=find_course(course_name)
        
        if user and course and not user.course:
            user.course_id=course.id
            try:
                db.session.commit()
            except:
                db.session.rollback()
            return jsonify({'course_name':user.course.name})            
        elif user.course:
            return jsonify({'course_name':user.course.name})
    else:
        return jsonify({'error':'missing information'})

@api.route('/add_course',methods=['POST'])
def add_course():
    data=request.json
    if data.get('course_name'):
        course_name=data.get('course_name')
        course=find_course(course_name)
        
        if course:
            return jsonify({'error':'course already exists'})     
        else:
            c=Courses(name='course_name')
            path=c.make_path(url_for('static')) 

            db.session.add(c)
            try:
                db.session.commit()
                return jsonify({'success':f'course added path is {path}'})
            except:
                db.session.rollback()
    else:
        return jsonify({'error':'missing information'})      

    

@api.route('/course_notes',methods=['GET'])
def course_notes():
    data=request.args.get('name')#recieve json inform of {'course_name':'name}
    if data :
        course_name=data
        notes=get_notes(course_name)
        if notes:
            return notes
        else:
            return jsonify({'error':'no notes found'})
            #send_ notes request email implementation
    else:
        return jsonify({'error':'course name needed'})


@api.route('/upload',methods=['POST'])            
def upload():
    if 'files' not in request.files:
        return jsonify({'error':' no file was chosen'})
    acronym=request.form.get('unit_prefix')
    for file in request.files.getlist('files'):
        res=savefile(file,acronym)
        if not res:
            return jsonify({'error':'unit not available'})
    return jsonify({'success':'request complete'})
        
@api.route('/get_units',methods=['GET'])
def get_units():
     units=Units.query.all()
     unit_names=[[{'acronym':unit.acronym,'name':unit.name,'year':unit.year,'semester':unit.semester}] for unit in units]
     return jsonify({'units':unit_names})



@api.route('/new_course',methods=['GET'])
def new_course():
    return render_template('addcourse.html')


@api.route('/find_notes',methods=['GET'])
def find_notes():
    return render_template('notes.html')
    

@api.route('/add_notes',methods=['GET'])
def add_notes():
    return render_template('upload.html')
            
            
