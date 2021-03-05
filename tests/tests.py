import unittest,os
from app.models import Users,Permissions,AnonymousUser,Courses,Units,Notes
from flask import current_app
from app import create_app,db

class BasicTestCase(unittest.TestCase):
    def setUp(self):
        self.app=create_app('testing')
        self.app_context=self.app.app_context()
        self.app_context.push()
        self.client=self.app.test_client()
        db.create_all()
        db.session.add(Courses(code='I39',name='Random'))
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        
        self.app_context.pop()
    def test_app_exists(self):
        self.assertFalse(current_app is None)
    def test_app_id_testing(self):
        self.assertTrue(current_app.config['TESTING'])
if __name__=='__main__':
    unittest.main()
        

   
