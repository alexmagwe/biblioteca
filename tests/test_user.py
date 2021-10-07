import unittest,os
from app.models import Users,Permissions,AnonymousUser,Courses,Units,Notes,AdminsList
from flask import current_app
from app import create_app,db
from app.auth import decode_auth_token,create_auth_token

class TestPermissions(unittest.TestCase):
    def setUp(self):
        self.password='random'
        self.app=create_app('testing')
        self.app_context=self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client=self.app.test_client(use_cookies=True)
        self.admin=AdminsList(email=os.environ.get('SUPER'))
        db.session.add(self.admin)
        db.session.commit()
        self.superuser=Users(email=os.environ.get('SUPER'),password=self.password)
        self.normaluser=Users(email='random@gmail.com',password=self.password)
        self.normaluser.set_password(self.password)
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
    def test_encode_auth_token(self):
        user = Users(
            email='test@test.com',
            username='test'
        )
        db.session.add(user)
        db.session.commit()
        token = create_auth_token(user.to_json())
        self.assertTrue(isinstance(token, str))
        # resp=self.client.get(url_for('api.'))

    def test_decode_auth_token(self):
        user = Users(
            email='test@test.com',
            username='test'
        )
        db.session.add(user)
        db.session.commit()
        auth_token = create_auth_token(user.to_json())
        self.assertTrue(isinstance(decode_auth_token(auth_token),dict))

    def test_registration(self):
        with self.client:
            response = self.client.post(
                '/api/signup',
                json={
                    'email':'joe@gmail.com',
                    'username':'joe',
                    'password':'123456'
                }
            )
            data=response.json
            self.assertTrue(data['type'] == 'success')
            self.assertTrue(isinstance(data['message'],str))
            self.assertTrue((data['data'],str))
            self.assertEqual(data['status'], 201)
    def test_token(self):
        with self.client:
            response = self.client.post(
                '/api/token',
                json={
                    'email':self.normaluser.email,
                }
            )
            data=response.json
            self.assertTrue(data['type'] == 'success')
            self.assertTrue((data['token'],str))
            
        with self.client:
            response = self.client.post(
                '/api/token',
                json={
                    'email':'rand@gmail.com',
                }
            )
            data=response.json
            self.assertTrue(data['type'] == 'success')
            self.assertTrue((data.get('token'),str))


