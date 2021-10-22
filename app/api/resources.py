from flask import Flask, jsonify, request, url_for, render_template, session, current_app
import requests
from flask_login import current_user
from .. import login_manager, db, getuploadpath
from . import api, myapi
import requests
import sys
from ..errorHandler import sendError, sendSuccess, sendWarning
from flask_restx import Resource, reqparse, fields
import os
import json
from sqlalchemy import exc
import jwt
from ..auth.drivemanager import Gdrive
from ..auth import decode_auth_token, create_auth_token
from ..decorators import token_required
from ..models import Courses, Units, Users, Notes, Categories, RoleReviewList, Permissions

drive = Gdrive()


def find_user(em):
    user = Users.query.filter_by(email=em).first()
    return user


def find_course(code):
    course = Courses.query.filter_by(code=code).first()
    return course


def find_unit(code):
    unit = Units.query.filter_by(code=code).first()
    if unit:
        return unit
    else:
        return None


def find_file(size):
    exists = Notes.query.filter_by(size=size).first()
    if exists:
        return True
    else:
        return False

# reason for passing code as a param even though its not used is for local server storage if its ever implemented

# this is not called anywhere
# def savefile(file, code='', toupload=False):
#     if toupload:#dont worry about what this means its probably a feature if we were using a local file database
#         path = getuploadpath()
#         try:
#             path = os.path.join(path, file.filename)
#             file.save(path)
#             return {'path': path}
#         except Exception as e:
#             return {'error': sys.exc_info()[0]}
#     return None
#     # create_new_path(unit)


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

searchparser = reqparse.RequestParser()
searchparser.add_argument("query", type=str, help='search query required')
#add course model
acmodel = myapi.model(
    'AddCourse', {'course_name': fields.String, 'course_code': fields.String})
#add user detaisl model
amcmodel = myapi.model(
    'AddUserDetails', {'course_code': fields.String, 'year': fields.String, 'semester': fields.String})
cnmodel = myapi.model('CourseNotes', {"course_code": fields.String})


# add_unit_model = myapi.model('AddUnits', {"units": fields.List(fields.Nested(unitfields))})
#unit notes model
unmodel = myapi.model('UnitNotes', {"unit_code": fields.String})
existsmodel = myapi.model('Exists', {"name": fields.String})
unitfields = myapi.model(
    'unitmodel', {"name": fields.String, "course_code": fields.String, "year": fields.Integer, "semester": fields.Integer, "code": fields.String})
#filter units model
fumodel = myapi.model(
    'FilterUnits', {"course_code": fields.String, "year": fields.Integer, "semester": fields.String,})

add_unit_model = myapi.model(
    'AddUnits', {"units": fields.List(fields.Nested(unitfields))})
notefield = myapi.model(
    'addcontent', {"name": fields.String, "gid": fields.String,"link":fields.String, "category": fields.String})
uploadmodel = myapi.model('AddContent', {"unit_code": fields.String, "files": fields.List(
    fields.Nested(notefield))})
searchmodel = myapi.model('Search', {"query": fields.String})


class Roles(Resource):
    def get(self):
        return sendSuccess(Permissions.roles)


class Search(Resource):
    @myapi.expect(searchmodel)
    @myapi.doc(body=searchmodel)
    def post(self):
        data = searchparser.parse_args()
        if (query := data.get("query")):
            res = drive.search(query)
            return sendSuccess(res)
        else:
            return sendError('empty query')
class FilterUnits(Resource):
    @myapi.expect(fumodel)
    def post(self):
        data=request.json
        year=data.get('year')
        semester=data.get('semester')
        course_code=data.get('course_code')
        if year and semester and course_code:
            course=find_course(course_code)
            if course:
                units=Units.query.filter_by(year=year,semester=semester,courses_id=course.id).all()
                return sendSuccess({"units":[unit.to_json() for unit in units]})  
        return sendError('Please provide the required information'),400
class UnitNotes(Resource):
    @myapi.expect(unmodel)
    @myapi.doc(body=unmodel)
    def post(self):
        data = unitparser.parse_args()
        if(code := data.get('unit_code')):
            unit = find_unit(code)
            if unit:
                notes = {Categories.DOCUMENT: [],
                         Categories.VIDEO: [], Categories.ASSIGNMENT: []}
                for note in unit.notes.order_by(Notes.name):
                    # metadata=drive.get_metadata(note.gid)
                    if note.category == Categories.DOCUMENT:
                        notes[Categories.DOCUMENT].append(note.to_json())
                    elif note.category == Categories.VIDEO:
                        notes[Categories.VIDEO].append(note.to_json())
                    elif note.category == Categories.ASSIGNMENT:
                        notes[Categories.ASSIGNMENT].append(note.to_json())
                    else:
                        notes[Categories.DOCUMENT].append(note.to_json())
                return sendSuccess({"unit": unit.name, "code": unit.code, 'notes': notes})
            else:
                return sendError('that unit doesn\'t exist or is not available yet')
        else:
            return sendError("invalid information recieved,expected json obj unit_code:string"), 400


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
                return sendSuccess(notes), 200
            else:
                return sendError('no notes found')
                # send_ notes request email implementation
        else:
            return sendError('course name needed'), 400


class AddCourse(Resource):
    @myapi.expect(acmodel)
    def post(self):
        data = request.json
        if (courses:=data.get('courses')):
            for course in data.get('courses'):
                course_code = course.get('course_code')
                course_name = course.get('course_name')
                if course_name and course_code:
                    course = find_course(course_code)
                    if course:
                        continue
                    else:
                        c = Courses(name=course_name, code=course_code)
                        db.session.add(c)
            try:
                db.session.commit()
                return sendSuccess('Courses added successfully')
            except:
                return sendError('Could not add courses,try again later')
        return sendError('invalid course information, expected json obj'),400


class AddContent(Resource):
    @myapi.expect(uploadmodel)
    def post(self):
        count = 0
        failed=[]
        data = request.json
        files = data.get('files')
        code = data.get('unit_code')
        if code:
            unit = find_unit(code)
            if unit and len(files) > 0:
                for f in files:

                    gid = f.get('gid')
                    link=f.get('link')
                    if gid and len(gid)>0:
                        if f.get("category") != Categories.VIDEO:
                            try:
                                # metadata contains name, size, webContentLink, webViewLink, iconLink, mimeType"
                                metadata = drive.get_metadata(gid, 'size')
                            except:
                                continue
                            if find_file(metadata.get('size')):
                                continue
                                fil = Notes(name=f.get('name'), gid=f.get(
                                'gid'), category=f.get('category'), unit_id=unit.id, size=metadata.get('size'))
                        else:
                            fil = Notes(name=f.get('name'), gid=f.get(
                                'gid'), category=f.get('category'), unit_id=unit.id)
                    elif link and len(link)>0:

                        fil = Notes(name=f.get('name'), link=f.get(
                            'link'), category=f.get('category'), unit_id=unit.id)
                    count += 1
            
                    db.session.add(fil)
                    try:
                        db.session.commit()
                    # return {"success":"notes added succesfully"}
                    except:
                        failed.append(f.get('name'))
                        db.session.rollback()
            else:
                return sendError('invalid unit')
        else:
            return sendError('unit code not found')
        if len(failed)>0:
            return sendWarning(f"some files {failed} could not be added due to naming conflicts"),500
        return sendSuccess('files added sucesfully'), 201


class AddUserDetails(Resource):
    @myapi.expect(amcmodel)
    @token_required
    def post(self):
        details = request.json
        user = find_user(request.user['email'])
        if not user:
            return sendError('if you see this message,something went horribly wrong,please contact me 0796914452')
        if (name := details.get('username')):
            user.username = name
        if(year := details.get('year')):
            user.year = year
        if(semester := details.get('semester')):
            user.semester = semester
        if (course_code := details.get('course_code')):
            course = find_course(course_code)
            if course:
                user.course_id = course.id
        try:
            db.session.commit()
            return user.to_json()
        except exc.IntegrityError:
            return sendError('Username already in use.')




# get details of the user course,user gotten from token

class UserDetails(Resource):
    @token_required
    def post(self):
        # token = request.headers.get('Authorization')
        if (data := request.user):
            em = data.get('email')
            user = find_user(em)
            return sendSuccess(user.to_json())
    # if the user course is not set or for some reason its not found, empty string will be returned
        else:
            return sendError("email not provided"),400


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
                return sendError('course unavailable')
        else:
            return sendError('course name not provided'), 400


class Exists(Resource):
    @myapi.expect(existsmodel)
    def post(self):
        data = request.json
        if (size := data.get('size')):
            res = find_file(size)
            return res
        else:
            return sendError('name not in request'), 400


# class AddUnit(Resource):
#     @myapi.doc(body=add_unit_model)
#     @myapi.expect(add_unit_model)
#     def post(self):
#         failed = []
#         data = request.json
#         if (units := data.get('units')):
#             if len(units) > 0:
#                 for unit in units:
#                     course = find_course(unit.get('course_code'))
#                     exists = find_unit(unit.get('unit_code'))
#                     if exists:
#                         continue
#                     if not course:
#                         failed.append(unit)
#                         continue

#                     u = Units(name=unit.get('name'), code=unit.get('unit_code'), semester=unit.get(
#                         'semester'), year=unit.get('year'), courses_id=course.id)
#                     db.session.add(u)
#         else:
#             return sendError("no units provided to add"), 400
#         try:
#             db.session.commit()
#             if len(failed) > 0:
#                 return sendError(f"the course information provided for the following units is invalid:{failed}")
#             return sendSuccess("units added succesfully")
#         except:
#             db.session.rollback()
class AddUnits(Resource):
    @myapi.doc(body=add_unit_model)
    @myapi.expect(add_unit_model)
    def post(self):
        failed = []
        count = 0
        data = request.json
        if (units := data.get('units')):
            if len(units) > 0:
                for unit in units:
                    course = find_course(unit.get('course_code'))
                    exists = find_unit(unit.get('code'))
                    if not course:
                        failed.append(unit.get("name"))
                        continue
                    if exists:
                        continue
                    u = Units(name=unit.get('name'), code=unit.get('code'), semester=unit.get(
                        'semester'), year=unit.get('year'), courses_id=course.id)
                    count += 1
                    db.session.add(u)
                try:
                    if count > 0:
                        db.session.commit()

                    if len(failed) > 0:
                        return sendError(f"the course code provided for the following units is invalid:{failed}")
                    return sendSuccess("units added succesfully")
                except Exception as e:
                    db.session.rollback()
                    return sendError("server error,please check the information provided"), 500
        else:
            return sendError("no units provided to add"), 400
