from flask import Flask,jsonify,request,url_for,render_template,session,current_app
import requests
from flask_login import current_user
from .. import login_manager,db,getuploadpath
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

def find_unit(code):
        unit=Units.query.filter_by(acronym=code).first()
        if unit:
            return (unit)
        else:
            return (None)     
        
def find_file(name):
    exists=Notes.query.filter_by(name=name).first()
    if exists:
        return True
    else:
        return False


    
# reason for passing code as a param even though its not used is for local server storage if its ever implemented
def savefile(file,code='',toupload=False):
    if toupload:
        path=getuploadpath()
        try:
            path=os.path.join(path,file.filename)
            file.save(path)
            return {'path':path}
        except Exception as e:
            return {'error':sys.exc_info()[0]}
    return None
            #create_new_path(unit)
def get_notes(course_name):
    course=find_course(course_name)
    notes=[]
    if course:
        units=course.units
        for unit in units:
            for n in unit.notes:
                notes.append({'unit':unit.acronym,'name':n.name,'gid':n.gid})
        if len(notes)>0:
            return notes
    else:
        return None


 


@api.route('/home')
@api.route('/')
def home():
    if current_user.is_authenticated:
        return render_template('landing.html',title='Biblioteca')
    else:
        return render_template('documentation.html',title='Biblioteca')

                           
@api.route('/new_course',methods=['GET'])
def new_course():
    return render_template('addcourse.html',title='Addcourse')


@api.route('/find_notes',methods=['GET'])
def find_notes():
    return render_template('notes.html',title='Notes')
    

@api.route('/upload_notes',methods=['GET'])
def upload_notes():
    return render_template('upload.html',title='Uploader')
# @api.route('/admin',methods=['GET','POST'])
# def adminpanel():
#     if current_user.is_authenticated and current_user.is_admin:
#         return render_template('admin/admin.html')
#     else:
#         return redirect(url_for('auth.home'))

parser=reqparse.RequestParser()
parser.add_argument('course_name',type=str,help='course name required')

unitparser=reqparse.RequestParser()
unitparser.add_argument('unit',type=str,help='unit acronym required')

acmodel=myapi.model('AddCourse',{'course_name':fields.String()})
cdmodel=myapi.model('CourseDetails',{'email':fields.String()})
amcmodel=myapi.model('AddMyCourse',{'email':fields.String(),'course_name':fields.String()})
cnmodel=myapi.model('CourseNotes',{'course_name':fields.String()})
unmodel=myapi.model('UnitNotes',{'unit_code':fields.String()})
# uploadmodel=myapi.model('Upload',{'headers':'unit'})

class UnitNotes(Resource):
    @myapi.expect(unmodel)
    @myapi.doc(body=unmodel)
    def post(self):
        data=unitparser.parse_args()
        print(data)
        if(code:=data.get('unit_code')):
            unit=find_unit(code)
            if unit:
                return {'notes':[note.name for note in unit.notes]}
            else:
                return {'error':'unit not found'}
        else:
            return {'error':"invalid information recieved,expected json obj unit:unit acronym"}
            
    
class CourseNotes(Resource):
    @myapi.expect(cnmodel)
    @myapi.doc(body=cnmodel)
    def post(self):
        data=parser.parse_args()
        data=data.get('course_name')
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
        if (course_name:=data.get('course_name')):
            course=find_course(course_name)
            if course:
                return {'message':'course already exists'}
            else:
                c=Courses(name='course_name')
                db.session.add(c)
                try:
                    db.session.commit()
                    return {'success':'course updated' }
                except:
                    db.session.rollback()
        else:
            return {'error':'invalid course information in request expected json obj {course name:string}'}

class Uploadlocal(Resource):
    def post(self):
        if 'files' not in request.files:
            return jsonify({'error':' no file was chosen'})
        acronym=request.form.get('unit_code')
        for file in request.files.getlist('files'):
            res=savefile(file,acronym)
            if not res:
                return jsonify({'error':'unit not available'})
            elif (error:=res.get('error')):
                return error    
        return jsonify({'success':'request complete'})  
     
class Upload(Resource):
    
    def post(self):
       
        files=request.files.getlist('notes')
        code=request.headers.get('unit_code') or request.form.get('unit_code')
        unit_id=find_unit(code).id
        print(unit_id)
        
        if files:
            creds=FileUploader.getcreds()
            for file in files:
                res=savefile(file,code,toupload=True)
                if res.get('error'):
                    return res,500
                if (path:=res.get('path')):
                    obj=FileUploader(path,file.filename,code)
                    exists=find_file(obj.name)
                    if exists:
                        continue
                    obj.driveupload(creds)
                    print(obj.id)
                    obj.delete_file()
                    if unit_id and obj.id:
                       note=Notes(name=obj.name,gid=obj.id,unit_id=unit_id)
                       db.session.add(note)
                       try:
                           db.session.commit()
                       except Exception as e:
                           print(e)
                           db.session.rollback()
                           return {'error':sys.exc_info()[0]}
                    else:
                        return {'error':'an error occured try again later'}
                    
        return {'success':'file(s) uploaded succesfully'}

      
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
        data=request.json
        if (em:=data.get('email')):
            user=find_user(em)
            if user and (course:=user.course):
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
    
class AllUnits(Resource):
    def get(self):
        units=Units.query.all()
        data=[{'code':unit.acronym,'name':unit.name,'year':unit.year,'semester':unit.semester} for unit in units]
        return data
class AllNotes(Resource):
    def get(self):
        notes=Notes.query.all()
        data=[{'name':note.name,"gid":note.gid,'unit':note.unit.name} for note in notes]
        return {"notes":data}    
class GetUnits(Resource):
    @myapi.expect(cnmodel)
    def post(self):
        data=request.json
        if (name:=data.get('course_name')):
            course=find_course(name)
            if course:
                return [{'acronym':unit.acronym,'name':unit.name,'year':unit.year,'semester':unit.semester} for unit in course.units]
            else:
                return {'error':'course unavailable'}
        else:
            return {'error':'course name not provided'}
            
        
myapi.add_resource(AllCourses,'/courses')
myapi.add_resource(CourseNotes,'/course_notes')
myapi.add_resource(AddCourse,'/add_course')
myapi.add_resource(CourseDetails,'/course_details')
myapi.add_resource(GetUnits,'/course_units')
myapi.add_resource(Upload,'/upload')
myapi.add_resource(AddMyCourse,'/add_mycourse')
myapi.add_resource(AllNotes,'/all_notes')
myapi.add_resource(UnitNotes,'/unit_notes')
myapi.add_resource(AllUnits,'/all_units')



