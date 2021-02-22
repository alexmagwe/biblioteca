from flask import Flask, jsonify, request, url_for, render_template, session, current_app
import requests
from flask_login import current_user
from .. import login_manager, db, getuploadpath
from . import api, myapi
import requests
import sys
from flask_restx import Resource, reqparse, fields
import os
import json
from ..auth.drivemanager import Gdrive
from ..models import Courses, Units, Users, Notes,Categories

drive=Gdrive()
def find_user(em):
    user = Users.query.filter_by(email=em).first()
    return user


def find_course(code):
    course = Courses.query.filter_by(code=code).first()
    return course


def find_unit(code):
    unit = Units.query.filter_by(code=code).first()
    if unit:
        return (unit)
    else:
        return (None)


def find_file(name):
    exists = Notes.query.filter_by(name=name).first()
    if exists:
        return True
    else:
        return False

# reason for passing code as a param even though its not used is for local server storage if its ever implemented


def savefile(file, code='', toupload=False):
    if toupload:
        path = getuploadpath()
        try:
            path = os.path.join(path, file.filename)
            file.save(path)
            return {'path': path}
            print('saved file')
            print(path)
        except Exception as e:
            print(e)
            return {'error': sys.exc_info()[0]}
    return None
    # create_new_path(unit)


def get_notes(course_code):
    course = find_course(course_code)
    notes = []
    if course:
        units = course.units  # change in model t olazy dynamic so i can query by year or semester
        for unit in units:
            for n in unit.notes:
                notes.append({'unit': unit.code, 'name': n.name, 'gid': n.gid})
        if len(notes) > 0:
            return notes
    else:
        return None


parser = reqparse.RequestParser()
parser.add_argument('course_code', type=str, help='course name required')

unitparser = reqparse.RequestParser()
unitparser.add_argument('unit_code', type=str, help='unit code required')

acmodel = myapi.model(
    'AddCourse', {'course_name': fields.String, 'course_code': fields.String})
cdmodel = myapi.model('CourseDetails', {'email': fields.String})
amcmodel = myapi.model(
    'AddMyCourse', {'email': fields.String, 'course_code': fields.String})
cnmodel = myapi.model('CourseNotes', {'course_code': fields.String})
aumodel = myapi.model('AddUnit', {'course_code': fields.String, 'name': fields.String,
                                  'semester': fields.String, 'unit_code': fields.String, 'year': fields.Integer})
unmodel = myapi.model('UnitNotes', {'unit_code': fields.String})
existsmodel = myapi.model('Exists', {'name': fields.String})
notefield = myapi.model('', {'name': fields.String, 'gid': fields.String})
uploadmodel = myapi.model('AddNotes', {'notes': fields.List(
    fields.Nested(notefield)), 'unit_code': fields.String})


class UnitNotes(Resource):
    @myapi.expect(unmodel)
    @myapi.doc(body=unmodel)
    def post(self):
        data = unitparser.parse_args()
        if(code := data.get('unit_code')):
            unit = find_unit(code)
            if unit:
                notes={Categories.DOCUMENT:[],Categories.VIDEO:[],Categories.ASSIGNMENT:[]}
                for note in unit.notes:
                    # metadata=drive.get_metadata(note.gid)
                    if note.category==Categories.DOCUMENT:
                        notes[Categories.DOCUMENT].append(note.to_json())
                    elif note.category==Categories.VIDEO:
                        notes[Categories.VIDEO].append(note.to_json())
                    elif note.category==Categories.ASSIGNMENT:
                        notes[Categories.ASSIGNMENT].append(note.to_json())
                    else:
                        notes[Categories.DOCUMENT].append(note.to_json())
                # print(notes)
                return {"unit": unit.name, "code": unit.code, 'notes': notes}
            else:
                return {'error': 'unit not found'}
        else:
            return {'error': "invalid information recieved,expected json obj unit:unit code"}


class CourseNotes(Resource):
    @myapi.expect(cnmodel)
    @myapi.doc(body=cnmodel)
    def post(self):
        data = parser.parse_args()
        data = data.get('course_code')
        if data:
            course_code = data
            notes = get_notes(course_code)
            if notes:
                return notes
            else:
                return {'error': 'no notes found'}
                # send_ notes request email implementation
        else:
            return {'error': 'course name needed'}


class AddCourse(Resource):
    @myapi.expect(acmodel)
    def post(self):
        data = request.json
        print('data recieved', data)
        course_code = data.get('course_code')
        course_name = data.get('course_name')
        if course_name and course_code:
            course = find_course(course_code)
            if course:
                return {'message': 'course already exists'}
            else:
                c = Courses(name=course_name, code=course_code)
                res = c.add()
                if res:
                    return {'success': 'course added'}
                else:
                    return {'error': 'could not create course,try again later'}
        else:
            return {'error': 'invalid course information in request expected json obj {course name:string}'}


class AddNotes(Resource):
    @myapi.expect(uploadmodel)
    def post(self):
        data = request.json
        notes = data.get('notes')
        code = data.get('unit_code')
        if code:
            unit = find_unit(code)
            if unit and len(notes) > 0:
                for note in notes:
                    if find_file(note.get('name')):
                        continue
                    gid=note.get('gid')
                    metadata=drive.get_metadata(gid,'size')#metadata contains name, size, webContentLink, webViewLink, iconLink, mimeType"
                    file = Notes(name=note.get('name'), gid=note.get(
                        'gid'), category=note.get('category'), unit_id=unit.id,size=int(metadata.get('size')))
                    db.session.add(file)
                try:
                    db.session.commit()
                    # return {"success":"notes added succesfully"}
                except Exception as e:
                    print(e)
                    return {'error': sys.exc_info()[0]}, 500
            else:
                return {'error': 'invalid unit'}, 400
        else:
            return {'error': 'unit code not found'}, 400
        return {'success': 'notes added sucesfully'}, 201


class AddMyCourse(Resource):
    @myapi.expect(amcmodel)
    def post(self):
        data = request.json
        if data.get('email') and data.get('course_code'):
            email = data['email']
            user = find_user(email)
            course_code = data.get('course_code')
            if not user:
                return {'error': 'user not found'}
            course = find_course(course_code)

            if user and course and not user.course:
                user.course_id = course.id
                try:
                    db.session.commit()
                except:
                    db.session.rollback()
                return {'name': user.course.name, 'code': course.code}
            elif user.course:
                return {'name': user.course.name, 'code': user.course.code}
        else:
            return {'error': 'missing email or course code'}

    def put(self):
        data = request.json
        if data.get('email') and data.get('course_code'):
            email = data['email']
            user = find_user(email)
            course_code = data.get('course_code')
            if not user:
                user = Users(email=em)
                res = user.add()
            course = find_course(course_code)

            user.course_id = course.id
            try:
                db.session.commit()
            except:
                db.session.rollback()
            return {'name': user.course.name, 'code': course.code}
        else:
            return {'error': 'missing email or course code'}


# get details of the student course,you supply the email
class CourseDetails(Resource):
    @myapi.expect(cdmodel)
    def post(self):
        data = request.json
        if (em := data.get('email')):
            user = find_user(em)
            if user and (course := user.course):
                # session['user']=user
                return {'name': course.name, 'code': course.code}
            elif not user:
                user = Users(email=em)
                res = user.add()
                if not res:
                    return {'error': 'user could not be created'}, 500
                # session['user']=user
                return {'course_name': None}, 404
            else:
                return {'course_name': None}, 404

    # if the user course is not set or for some reason its not found empty string will be returned
        else:
            return {'error': "email not provided"}


class AllCourses(Resource):
    def get(self):
        courses = Courses.query.all()
        data = [course.to_json() for course in courses]
        return data


class AllUnits(Resource):
    def get(self):
        units = Units.query.all()
        data = [unit.to_json() for unit in units]
        return data


class AllNotes(Resource):
    def get(self):
        notes = Notes.query.all()
        data = [note.to_json() for note in notes]
        return {"notes": data}


class GetUnits(Resource):
    @myapi.expect(cnmodel)
    def post(self):
        data = request.json
        if (code := data.get('course_code')):
            course = find_course(code)
            if course:
                if (year := data.get('year')):
                    return [unit.to_json() for unit in course.units.filter_by(year=year).all()]
                else:
                    return [unit.to_json() for unit in course.units]

            else:
                return {'error': 'course unavailable'}, 404
        else:
            return {'error': 'course name not provided'}, 400


class Exists(Resource):
    @myapi.expect(existsmodel)
    def post(self):
        data = request.json
        print(data)
        if (name := data.get('name')):
            res = find_file(name)
            return res
        else:
            return{'error': 'name not in request'}, 400


class AddUnit(Resource):
    @myapi.expect(aumodel)
    def post(self):
        print(request.json)
        data = request.json
        if data.get('course_code') and data.get('name') and data.get('unit_code') and data.get('semester') and data.get('year'):
            unit = find_unit(data.get('unit_code'))

            course = find_course(data.get('course_code'))
            print(course)
            if unit:
                return
            elif not unit and course:
                u = Units(name=data.get('name'), code=data.get('unit_code'), semester=data.get(
                    'semester'), year=data.get('year'), courses_id=course.id)
                res = u.add()
                if res:
                    return {'message': 'added sucessfully'},201
                else:
                    return {'error': 'try again later'}, 500
            elif not unit and not course:
                return {'error': f"{data.get('course_name')} not found"}, 400
            else:
                return
        else:
            return {'error': 'missing information'}, 500
