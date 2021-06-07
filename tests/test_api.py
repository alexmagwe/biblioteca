import unittest,os,sys,json
from app import create_app,db
from app.models import Notes,Units,Courses,Users 
from app.api.resources import find_user,find_course,find_unit,find_file

class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app=create_app('testing')
        self.app_context=self.app.app_context()
        self.app_context.push()
        self.client=self.app.test_client(use_cookies=True)
        self.test_email="test_user@example.com"
        db.create_all()
        c=Courses(code='I39',name='Random')
        unit=Units(name='Random name',code='SPH207',year='2',semester='1')
        user=Users(email=self.test_email)
        db.session.add(user)
        db.session.add(unit)
        db.session.add(c)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_find_course(self):
        test_code=['I39','I44']
        self.assertIsNotNone(Courses.query.all())
        self.assertTrue(find_course(test_code[0]))
        self.assertFalse(find_course(test_code[1]))
    
    def test_find_unit(self):
        test_code=['SPH207','SPH313']
        self.assertIsNotNone(find_unit(test_code[0]))
        self.assertIsNone(find_unit(test_code[1]))
    
    # def test_find_note(self):
    #     test_code=['162364','100010']
    #     self.assertTrue(find_course(test_code[0]))
    #     self.assertFalse(find_course(test_code[1]))
    
    def test_get_course_notes(self):
        url='/api/course/notes/all'
        response=self.client.post(url,data={'body':""})
        self.assertEqual(response.status_code,400)
        response=self.client.post(url,data={"course_code":""})
        self.assertEqual(response.status_code,400)
        response=self.client.post(url,data={"course_code":"I39"})
        self.assertEqual(response.status_code,200)
        
    def test_get_unit_notes(self):
        url='/api/unit/notes/all'
        response=self.client.post(url,data={'body':""})
        self.assertEqual(response.status_code,400)
        response=self.client.post(url,data={"unit_code":"rand321"})
        self.assertEqual(response.status_code,404)
        response=self.client.post(url,data={"unit_code":"SPH207"})
        self.assertEqual(response.status_code,200)
        
    def test_get_course_details(self):
        url='/api/course/details'
        response=self.client.post(url,data={"email":"some@example.com"})
        self.assertEqual(response.status_code,201)
        response=self.client.post(url,data={"email":self.test_email})
        self.assertEqual(response.status_code,404)
    
    def test_add_video_content(self):
        url='/api/add/content'
        response=self.client.post(url,data={"unit_code":"SPH207","files":[{"name":"lecture 1","gid":"mb vkljietnhnmlk4t66myu4","category":"video"}]})
        self.assertEqual(response.status_code,201)
        response=self.client.post(url,data={"unit_code":"SPH323","files":[{"name":"lecture 1","gid":"mb vkljietnhnmlk4t66myu4"}]})
        self.assertEqual(response.status_code,500)
        response=self.client.post(url,data={"unit_code":"SPH323","files":[{"name":"lecture 1","gid":"mb vkljietnhnmlk4t66myu4","category":"document"}]})
        self.assertEqual(response.status_code,500)
        
        
    
    
        
    
