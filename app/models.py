from . import db,login_manager,admin
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin,AnonymousUserMixin,current_user
from flask import current_app,redirect,url_for
from passlib.hash import sha256_crypt
import os

class Permissions:
    ADMIN=16
    ADDNOTES=8
    MYNOTES=4
       
@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))
class Users(db.Model,UserMixin):
    id=db.Column(db.Integer,unique=True,primary_key=True,autoincrement=True)
    email=db.Column(db.String(30),unique=True,nullable=False)
    permissions=db.Column(db.Integer,default=Permissions.MYNOTES)
    password=db.Column(db.String(100))
    course_id=db.Column(db.Integer,db.ForeignKey('courses.id'))
    #year
    def __init__(self,*args,**kwargs):
        super(Users,self).__init__(*args,**kwargs)
        if self.permissions is None:
            teacher=Teachers.query.filter_by(email=self.email).first()
            admin=AdminsList.query.filter_by(email=self.email).first()
            if teacher:
                self.permissions=Permissions.ADDNOTES+Permissions.MYNOTES
            if admin:
                self.permissions=Permissions.ADMIN+Permissions.ADDNOTES+Permissions.MYNOTES
            
    def can(self,perm):
        return self.permissions is not None and self.has_permission(perm)
    def has_permission(self,p):
        return self.permissions&p==p#BITWISE AND COMPARISON  OF  INPUT AND SELF.PERM
    @property
    def is_admin(self):
        return self.can(Permissions.ADMIN)
    
    def __repr__(self):
        return f'email:{self.email},permissions:{self.permissions}'
    
    def set_password(self,password):
        self.password=sha256_crypt.encrypt(password)
        
    def verify_password(self,password):
        return sha256_crypt.verify(password,self.password)
    
class AnonymousUser(AnonymousUserMixin):
    def can(self,perm):
        return False
    @property
    def is_admin(self):
        return False
login_manager.anonymous_user=AnonymousUser
class AdminsList(db.Model):
    id=db.Column(db.Integer,unique=True,primary_key=True,autoincrement=True)
    email=db.Column(db.String(100),unique=True,nullable=False)
    def __repr__(self):
        return f"{self.email}"
    def add(self):
        db.session.add(self)
        try:
            db.session.commit()
            return {'success':'admin addded succesfully'}
        except Exception as e:
            return {'error':e}
        

class Teachers(db.Model):
    id=db.Column(db.Integer,unique=True,primary_key=True,autoincrement=True)
    email=db.Column(db.String(30),index=True,nullable=False)
    def __repr__(self):
        return f'email:{self.email}'
    
class Courses(db.Model):
    id=db.Column(db.Integer,unique=True,primary_key=True,autoincrement=True)
    name=db.Column(db.String(100),unique=True,index=True)
    units=db.relationship('Units',backref='courses')
    users=db.relationship('Users',backref='course',lazy=True)#to allow pagination set lazy='dynamic'

    def __repr__(self):
        return f'course:{self.name},no of units:{len(self.units)} no of students:{len(self.users )}'
    

class Units(db.Model):
    id=db.Column(db.Integer,unique=True,primary_key=True,autoincrement=True)
    name=db.Column(db.String(100),unique=True,index=True,nullable=False)
    acronym=db.Column(db.String(10),unique=True,index=True)
    notes=db.relationship('Notes',backref='unit',lazy=True)
    semester=db.Column(db.String(10),index=True)
    year=db.Column(db.Integer,index=True)
    courses_id=db.Column(db.Integer,db.ForeignKey('courses.id'))
    def __repr__(self):
        return f'unit:{self.acronym},year:{self.year},semester:{self.semester},no of notes:{len(self.notes)}'
   

class Notes(db.Model):
    id=db.Column(db.Integer,unique=True,primary_key=True,autoincrement=True)
    name=db.Column(db.String(100),unique=True,index=True)
    unit_id=db.Column(db.Integer,db.ForeignKey('units.id'),nullable=False)
    gid=db.Column(db.String(),unique=True,index=True)

    def __repr__(self):
       return f'notes:{self.name},unit-name:[{self.unit.name}]'
  
    
        
        

class AdminView(ModelView):
    def __init__(self,*kwargs):
        super().__init__(*kwargs)
    column_exclude_list = ['password']
    def is_accessible(self):
        return current_user.is_admin
    def inaccessible_callback(self, name, **kwargs):
        print('inacessible')
        if not self.is_accessible():
            return redirect(url_for('api.home'))


# admin.add_view(AdminView(Users,db.session))
# admin.add_view(AdminView(Courses,db.session))
# admin.add_view(AdminView(Units,db.session))
admin.add_view(AdminView(AdminsList,db.session))
admin.add_view(AdminView(Teachers,db.session))

admin.add_view(AdminView(Courses,db.session))
admin.add_view(AdminView(Users,db.session))
admin.add_view(AdminView(Units,db.session))
admin.add_view(AdminView(Notes,db.session))