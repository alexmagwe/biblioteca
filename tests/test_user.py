import unittest,os
from app.models import Users,Permissions,AnonymousUser,Courses,Units,Notes,AdminsList
from flask import current_app
from app import create_app,db

class TestPermissions(unittest.TestCase):
    def setUp(self):
        self.app=create_app('testing')
        self.app_context=self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.admin=AdminsList(email=os.environ.get('SUPER'))
        db.session.add(self.admin)
        db.session.commit()
        self.superuser=Users(email=os.environ.get('SUPER'),password='random')
        self.normaluser=Users(email='random@gmail.com',password='random')
        db.session.add(self.normaluser)
        db.session.add(self.superuser)
        db.session.commit()
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()        
        
    def test_normal_user(self):
        user=Users.query.filter_by(email='random@gmail.com').first()
        
        self.assertFalse(user.can(Permissions.roles["SUPER_ADMIN"]))
        self.assertFalse(user.can(Permissions.roles["ADMIN"]))
        self.assertFalse(user.can(Permissions.roles["LECTURER"]))
        self.assertFalse(user.can(Permissions.roles["MODERATOR"]))
        self.assertTrue(user.can(Permissions.roles["USER"]))
        
    def test_anonymous_user(self):
        user=AnonymousUser()
        self.assertFalse(user.can(Permissions.roles["SUPER_ADMIN"]))
        self.assertFalse(user.can(Permissions.roles["ADMIN"]))
        self.assertFalse(user.can(Permissions.roles["LECTURER"]))
        self.assertFalse(user.can(Permissions.roles["MODERATOR"]))
        self.assertFalse(user.can(Permissions.roles["USER"]))
        
    def test_admin(self):
        user=Users.query.filter_by(email=os.environ.get('SUPER')).first()
        self.assertTrue(user.can(Permissions.roles["SUPER_ADMIN"]))
        self.assertTrue(user.can(Permissions.roles["ADMIN"]))
        self.assertTrue(user.can(Permissions.roles["LECTURER"]))
        self.assertTrue(user.can(Permissions.roles["MODERATOR"]))
        self.assertTrue(user.can(Permissions.roles["USER"]))
        
        
        # resp=self.client.get(url_for('api.'))
        
        