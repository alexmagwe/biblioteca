from flask import Flask,jsonify,request,url_for,render_template,session,current_app
import requests
from notes01.app import login_manager,db,getuploadpath
from . import api,myapi
import requests,sys
from flask_restx import Resource,reqparse,fields
import os,json
from .upload import FileUploader
from ..models import Courses,Units,Users,Notes

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
        

              
def savefile(file,unit_prefix='',toupload=False):
    if toupload:
        path=getuploadpath()
        print(path)
        try:
            path=os.path.join(path,file.filename)
            file.save(path)
            return {'path':path}
        except Exception as e:
            print(e)
            return {'error':sys.exc_info()[0]}
    else:
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
            except Exception as e:
                return {'error':e}
                
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


 


@api.route('/new_course',methods=['GET'])
def new_course():
    return render_template('addcourse.html')


@api.route('/find_notes',methods=['GET'])
def find_notes():
    return render_template('notes.html')
    

@api.route('/upload_notes',methods=['GET'])
def upload_notes():
    return render_template('upload.html')

parser=reqparse.RequestParser()
parser.add_argument('course_name',type=str,help='course name required')

acmodel=myapi.model('AddCourse',{'name':fields.String()})
cdmodel=myapi.model('CourseDetails',{'email':fields.String()})
amcmodel=myapi.model('AddMyCourse',{'email':fields.String(),'course_name':fields.String()})
cnmodel=myapi.model('CourseNotes',{'course_name':fields.String()})

class CourseNotes(Resource):
    @myapi.expect(cnmodel)
    @myapi.doc(body=cnmodel)
    def post(self):
        data=parser.parse_args()
        print(data)
        data=data.get('course_name')
        print(data)
        if data:
            course_name=data
            notes=get_notes(course_name)
            if notes:
                return notes
            else:
                return {'error':'no notes found'}
                #send_ notes request email implementation
        else:
            return {'error':'course name needed'}
class AddCourse(Resource):
    @myapi.expect(acmodel)
    def post(self):
        data=request.json
        if data.get('course_name'):
            course_name=data.get('course_name')
            course=find_course(course_name)
            if course:
                return {'error':'course already exists'}
            else:
                c=Courses(name='course_name')
                path=c.make_path(url_for('static')) 

                db.session.add(c)
                try:
                    db.session.commit()
                    return {'success':f'course added path is {path}'}
                except:
                    db.session.rollback()
        else:
            return {'error':'missing information'}

class Uploadlocal(Resource):
    def post(self):
        if 'files' not in request.files:
            return jsonify({'error':' no file was chosen'})
        acronym=request.form.get('unit_prefix')
        for file in request.files.getlist('files'):
            res=savefile(file,acronym)
            if not res:
                return jsonify({'error':'unit not available'})
            elif (error:=res.get('error')):
                return error    
        return jsonify({'success':'request complete'})   
class Upload(Resource):
    def post(self):
        uploaded=[]
        files=request.files.getlist('notes')
        unit=request.headers.get('unit')     
        if files:
            drive=FileUploader.getDrive()
            for file in files:
                print(file)
                res=savefile(file,unit,toupload=True)
                print(res)
                if res.get('error'):
                    print('\n\n',res)
                    return res,500
                if (path:=res.get('path')):
                    obj=FileUploader(path,file.filename,unit)
                    obj.driveupload(drive)
                    obj.delete_file()
                    res=obj.getResource(drive)
                    if res:
                        print('got data')
                        uploaded.append(obj.data)
                    
        return uploaded

    

class AddMyCourse(Resource):
    @myapi.expect(amcmodel)
    def post(self):
        data=request.json 
        if data.get('email') and data.get('course_name'):
            email=data['email']
            if 'user' in session:
                user=session.get('user')
            else:
                user=find_user(email)
            print('user',user)
            course_name=data.get('course_name')
            if user:
                email=user.email
            else: 
                return {'error':'user not found'}
            course=find_course(course_name)
            
            if user and course and not user.course:
                user.course_id=course.id
                try:
                    db.session.commit()
                except:
                    db.session.rollback()
                return {'course_name':user.course.name}         
            elif user.course:
                return {'course_name':user.course.name}
        else:
            return {'error':'missing information'}
        
# get details of the student course,you supply the email
class CourseDetails(Resource):
    @myapi.expect(cdmodel)
    def post(self):
        print('data recieved')
        data=request.json
        print(data)
            
        if (em:=data.get('email')):
            user=find_user(em)
            if user and (course:=user.course):
                print('user and course found')
                # session['user']=user
                return {'course':course.name}
            elif not user:
                user=Users(email=em)
                db.session.add(user)
                try:
                    db.session.commit()
                except:
                    db.session.rollback()
                    return {'error':'user could not be created'}
                # session['user']=user
                print('new user created')
                return {'course_name':None}
            else:
                return {'course_name':None}
                
    #if the user course is not set or for some reason its not found empty string will be returned          
        else:
            return {'error':"email not provided"}
class AllCourses(Resource):
    def get(self):
        courses=Courses.query.all()
        data=[course.name for course in courses]
        return {"courses":data}
class AllNotes(Resource):
    
    def get(self):
        notes=Notes.query.all()
        data=[{'name':note.name,"url":"/".join(note.path.split('/')[-8:]),'unit':note.unit.name} for note in notes]
        return {"notes":data}    
class GetUnits(Resource):
    @myapi.expect(cnmodel)
    def post(self):
        data=request.json
        if (name:=data.get('course_name')):
            course=find_course(name)
            if course:
                return {course.name:[unit.acronym for unit in course.units]}
            else:
                return {'error':'course unavailable'}
        else:
            return {'error':'course name not provided'}
            
        
myapi.add_resource(AllCourses,'/courses')
myapi.add_resource(CourseNotes,'/course_notes')
myapi.add_resource(AddCourse,'/add_course')
myapi.add_resource(CourseDetails,'/course_details')
myapi.add_resource(GetUnits,'/units')
myapi.add_resource(Upload,'/add_notes')
myapi.add_resource(AddMyCourse,'/add_mycourse')
myapi.add_resource(AllNotes,'/all_notes')

