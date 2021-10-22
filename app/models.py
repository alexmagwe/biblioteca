from . import db, login_manager, admin
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, AnonymousUserMixin, current_user
from flask import current_app, redirect, url_for
from passlib.hash import sha256_crypt
import os
import functools
import requests
import json
import datetime


class Permissions:
    roles = {"SUPER_ADMIN": 20,
             "ADMIN": 16,
             "LECTURER": 12,
             "MODERATOR": 8,
             "USER": 4}


@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))


class Utilities:
    def add(self):
        db.session.add(self)
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False

    def sync_remote_db():
        print("synchronizing local database with remote one...")
        print("updating courses...")
        resp = requests.get(
            "https://uon-notes-api.herokuapp.com/api/courses/all")
        if resp:
            data = resp.json()
            if (courses := data):
                print(f"found {len(courses)} courses")
                for course in courses:
                    if Courses.query.filter_by(code=course['code']).first():
                        continue
                    c = Courses(name=course.get("name"),
                                code=course.get("code"))
                    db.session.add(c)
        try:
            db.session.commit()
            print("Courses added succesfully!")
        except Exception as err:
            raise err

        all_courses = Courses.query.all()
        if all_courses:
            print(f'\nupdating units for {len(all_courses)} courses...')
            for c in all_courses:
                resp = requests.post(
                    "https://uon-notes-api.herokuapp.com/api/course/units", json={"course_code": c.code})
                if resp:
                    data = resp.json()
                    if data:
                        print(f'found {len(data)} units for {c.name}...')
                        for unit in data:
                            if Units.query.filter_by(code=unit['code']).first():
                                continue
                            u = Units(name=unit['name'], code=unit['code'],
                                      year=unit['year'], semester=unit['semester'], courses_id=c.id)
                            db.session.add(u)
            try:
                db.session.commit()
                print("Units added succesfully!")
            except Exception as err:
                raise err

        units = Units.query.all()
        if units:
            print("updating Unit contents...")
            for unit in units:
                resp = requests.post(
                    "https://uon-notes-api.herokuapp.com/api/unit/notes/all", json={"unit_code": unit.code})
                if resp:
                    data = resp.json()
                    if (notes := data.get("notes")):
                        print(notes.values())
                        try:
                            total = functools.reduce(
                                lambda a, b: a+b, notes.values())
                        except TypeError:
                            continue
                        print(f'found {len(total)} files for {unit.code}...')
                        for category in notes.values():
                            for item in category:
                                if Notes.query.filter_by(name=item['name']).first():
                                    continue
                                n = Notes(name=item.get("name"), unit_id=unit.id, gid=item.get(
                                    "gid"), category=item.get("category"), size=item.get("size"))
                                db.session.add(n)
            try:
                db.session.commit()
                print("Content added succesfully!")
            except Exception as err:
                raise err
            print("\n\ndatabase successfully synchronized!")


class Categories:
    DOCUMENT = 'document'
    VIDEO = 'video'
    ASSIGNMENT = 'assignment'


class Users(db.Model, UserMixin, Utilities):
    id = db.Column(db.Integer, unique=True,
                   primary_key=True, autoincrement=True)
    email = db.Column(db.String(30), unique=True, nullable=False)
    role = db.Column(db.Integer, default=Permissions.roles["USER"])
    password = db.Column(db.String(100))
    year = db.Column(db.Integer)
    username = db.Column(db.String(30), unique=True, index=True)
    semester = db.Column(db.Integer)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    joined_date = db.Column(db.DateTime, index=True,
                            default=datetime.datetime.utcnow)
    # year

    def __init__(self, *args, **kwargs):
        super(Users, self).__init__(*args, **kwargs)
        if self.role is None:
            admin = AdminsList.query.filter_by(email=self.email).first()
            if admin:
                self.role = Permissions.roles["SUPER_ADMIN"]

    def to_json(self):
        if self.course:
            return {"email": self.email, "role": self.role, "username": self.username, "year": self.year, "semester": self.semester, "date_joined": str(self.joined_date), "course": self.course.to_json()}
        else:
            return {"email": self.email, "role": self.role, "username": self.username, "year": self.year, "semester": self.semester, "date_joined": str(self.joined_date), "course": None}

    def can(self, perm):
        return self.role is not None and self.has_permission(perm)

    def has_permission(self, p):
        return self.role >= p

    @property
    def is_admin(self):
        return self.can(Permissions.roles["SUPER_ADMIN"])

    def __repr__(self):
        role = [r for r in Permissions.roles if Permissions.roles[r] == self.role]
        return f'email:{self.email},role:{role}'

    def set_password(self, password):
        self.password = sha256_crypt.encrypt(password)

    def verify_password(self, password):
        return sha256_crypt.verify(password, self.password)


class AnonymousUser(AnonymousUserMixin):
    def can(self, perm):
        return False

    @property
    def is_admin(self):
        return False


login_manager.anonymous_user = AnonymousUser


class AdminsList(db.Model, Utilities):
    id = db.Column(db.Integer, unique=True,
                   primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"{self.email}"


class RoleReviewList(db.Model, Utilities):
    id = db.Column(db.Integer, unique=True,
                   primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    date = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    current_role = db.Column(db.Integer(), nullable=False,
                             index=True, default=Permissions.roles["USER"])
    requested_role = db.Column(db.Integer(), nullable=False, index=True)
    request_date = db.Column(db.DateTime, index=True,
                             default=datetime.datetime.utcnow)

    def __repr__(self):
        # get role string definition from matching value
        curr_role == [
            r for r in Permissions.roles if Permissions.roles[r] == self.current_role]
        req_role == [
            r for r in Permissions.roles if Permissions.roles[r] == self.requested_role]
        return f"email:{self.email},current role:{curr_role},requested_role:{req_role}"

    def approve_or_decline(self, approved):
        u = Users.query.filter_by(email=self.email).first()
        if u and approved:
            u.role = self.requested_role
            db.session.commit()
            return True
        return False


class Courses(db.Model, Utilities):
    id = db.Column(db.Integer, unique=True,
                   primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    units = db.relationship('Units', backref='courses', lazy='dynamic')
    code = db.Column(db.String(10), unique=True, index=True, nullable=False)
    # to allow pagination and also to return a query obj set lazy='dynamic'
    users = db.relationship('Users', backref='course', lazy=True)

    def __repr__(self):
        return f'course:{self.name}'

    def to_json(self):
        return {'name': self.name, 'code': self.code}


class Units(db.Model, Utilities):
    id = db.Column(db.Integer, unique=True,
                   primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, index=True, nullable=False)
    code = db.Column(db.String(10), unique=True, index=True, nullable=False)
    notes = db.relationship('Notes', backref='unit', lazy="dynamic")
    semester = db.Column(db.String(10), index=True, nullable=False)
    year = db.Column(db.Integer, index=True, nullable=False)
    courses_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

    def __repr__(self):
        return f'id:{self.id},unit:{self.code},year:{self.year},semester:{self.semester},no of notes:{len(self.notes.all())}'

    def to_json(self):
        return {'code': self.code, 'name': self.name, 'year': self.year, 'semester': self.semester}

    @staticmethod
    def generate(course_id='I39'):
        course_id = course_id.upper()
        id = Courses.query.filter_by(code=course_id).first()
        with open(os.path.abspath('units.json')) as f:
            data = json.load(f)

            for unit in data:
                if not Units.query.filter_by(code=unit['code']).first():
                    u = Units(name=unit['name'], code=unit['code'],
                              year=unit['year'], semester=unit['semester'], courses_id=id)
                    print(f'adding {u.code}')
                    db.session.add(u)
            try:
                db.session.commit()
                print('success')
            except:
                db.session.rollback()


class Notes(db.Model, Utilities):
    id = db.Column(db.Integer, unique=True,
                   primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, index=True)
    unit_id = db.Column(db.Integer, db.ForeignKey('units.id'), nullable=False)
    gid = db.Column(db.String(), unique=True, index=True)
    link = db.Column(db.String(), unique=True, index=True)
    category = db.Column(db.String(20), default=Categories.DOCUMENT)
    size = db.Column(db.String(), unique=True, index=True)
    date_uploaded = db.Column(db.DateTime, index=True,
                              default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'notes:{self.name}'

    def to_json(self):
        return {"id": self.id, "name": self.name, "gid": self.gid, "link": self.link, "category": self.category}

    def delete_file(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except:
            return False

    def get_unit(self):
        unit = Units.query.filter_by(id=self.unit_id)
        return unit


class AdminView(ModelView):
    def __init__(self, *kwargs):
        super().__init__(*kwargs)
    column_exclude_list = ['password']

    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        print('inacessible')
        if not self.is_accessible():
            return redirect(url_for('api.home'))


class NotesView(ModelView):
    column_searchable_list = (Notes.name, Notes.category, Notes.unit_id)

    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('api.home'))


class CoursesView(ModelView):
    column_searchable_list = (Courses.name, Courses.code)

    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('api.home'))


class UnitsView(ModelView):
    column_searchable_list = (Units.name, Units.code)

    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('api.home'))


class RoleReviewListView(ModelView):
    column_searchable_list = (
        RoleReviewList.requested_role, RoleReviewList.email)

    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('api.home'))


admin.add_view(AdminView(AdminsList, db.session))
admin.add_view(CoursesView(Courses, db.session))
admin.add_view(RoleReviewListView(RoleReviewList, db.session))
admin.add_view(AdminView(Users, db.session))
admin.add_view(UnitsView(Units, db.session))
admin.add_view(NotesView(Notes, db.session))
