from . import db, login_manager, admin
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, AnonymousUserMixin, current_user
from flask import current_app, redirect, url_for
from passlib.hash import sha256_crypt
import os
import sys
import json
from datetime import datetime


class Permissions:
    ADMIN = 16
    MODERATE = 12
    ADDNOTES = 8
    MYNOTES = 4


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
            return False


class Categories:
    DOCUMENT = 'document'
    VIDEO = 'video'
    ASSIGNMENT = 'assignment'


class Users(db.Model, UserMixin, Utilities):
    id = db.Column(db.Integer, unique=True,
                   primary_key=True, autoincrement=True)
    email = db.Column(db.String(30), unique=True, nullable=False)
    permissions = db.Column(db.Integer, default=Permissions.MYNOTES)
    password = db.Column(db.String(100))
    year = db.Column(db.Integer)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    # year

    def __init__(self, *args, **kwargs):
        super(Users, self).__init__(*args, **kwargs)
        if self.permissions is None:
            admin = AdminsList.query.filter_by(email=self.email).first()
            if admin:
                self.permissions = Permissions.ADMIN+Permissions.ADDNOTES+Permissions.MYNOTES

    def can(self, perm):
        return self.permissions is not None and self.has_permission(perm)

    def has_permission(self, p):
        return self.permissions >= p

    @property
    def is_admin(self):
        return self.can(Permissions.ADMIN)

    def __repr__(self):
        return f'email:{self.email},permissions:{self.permissions}'

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


class Courses(db.Model, Utilities):
    id = db.Column(db.Integer, unique=True,
                   primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, index=True)
    units = db.relationship('Units', backref='courses', lazy='dynamic')
    code = db.Column(db.String(10), unique=True, index=True)
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
    code = db.Column(db.String(10), unique=True, index=True)
    notes = db.relationship('Notes', backref='unit', lazy="dynamic")
    semester = db.Column(db.String(10), index=True)
    year = db.Column(db.Integer, index=True)
    courses_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

    def __repr__(self):
        return f'id:{self.id},unit:{self.code},year:{self.year},semester:{self.semester},no of notes:{len(self.notes.all())}'

    def to_json(self):
        return {'code': self.code, 'name': self.name, 'year': self.year, 'semester': self.semester}

    @staticmethod
    def generate(course_id='I39'):
        course_id=course_id.upper()
        id = Courses.query.filter_by(code=course_id).first()
        with open(os.path.abspath('units.json')) as f:
            data = json.load(f)
            for unit in data:
                if not Units.query.filter_by(code=unit['code']).first():
                    u = Units(name=unit['name'], code=unit['code'],year=unit['year'], semester=unit['semester'], courses_id=id)
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
    category = db.Column(db.String(20), default=Categories.DOCUMENT)
    size=db.Column(db.String(),unique=True,index=True)
    date_uploaded = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'notes:{self.name}'

    def to_json(self):
        return {"id": self.id, "name": self.name, "gid": self.gid, "category": self.category}
    def delete_file(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except:
            return False

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
    column_searchable_list = (Notes.name, Notes.category,Notes.unit_id)

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


admin.add_view(AdminView(AdminsList, db.session))
admin.add_view(CoursesView(Courses, db.session))
admin.add_view(AdminView(Users, db.session))
admin.add_view(UnitsView(Units, db.session))
admin.add_view(NotesView(Notes, db.session))
