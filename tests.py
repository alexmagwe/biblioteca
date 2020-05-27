import unittest
from app.models import Users,Permissions,AnonymousUser
class TestPermissions(unittest.TestCase):
    def test_role(self):
        user=Users(email='alexmage@gmail.com',username='alex',password='random')
        self.assertFalse(user.can(Permissions.ADDNOTES))
        self.assertFalse(user.can(Permissions.ADMIN))
        self.assertTrue(user.can(Permissions.MYNOTES))
        
    def test_anonymous_user(self):
        user=AnonymousUser()
        self.assertFalse(user.can(Permissions.ADDNOTES))
        self.assertFalse(user.can(Permissions.ADMIN))
        self.assertFalse(user.can(Permissions.MYNOTES))
        
    def test_admin(self):
        user=Users(email='alexmagwe@gmail.com',username='admin',password='cat')
        self.AssertTrue(user.can(Permissions.ADDNOTES))
        self.AssertTrue(user.can(Permissions.ADMIN))
        self.AssertTrue(user.can(Permissions.MYNOTES))
        
        
if __name__=='__main__':
    unittest.main()
