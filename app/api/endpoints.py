from . import myapi
from .resources import AddUnits, AddCourse, CourseNotes, AllCourses, AllNotes, AddUserDetails, AddContent, Roles, CourseDetails, AllUnits, GetUnits, UnitNotes, Exists, Search

myapi.add_resource(AllCourses, '/courses/all')
myapi.add_resource(CourseNotes, '/course/notes/all')
myapi.add_resource(AddCourse, '/add/course')
myapi.add_resource(CourseDetails, '/course/details')
myapi.add_resource(GetUnits, '/course/units')
myapi.add_resource(AddContent, '/add/content')
myapi.add_resource(AddUserDetails, '/add/mycourse')
myapi.add_resource(AllNotes, '/notes/all')
myapi.add_resource(UnitNotes, '/unit/notes/all')
myapi.add_resource(AllUnits, '/units/all')
myapi.add_resource(AddUnits, '/add/units')
myapi.add_resource(Exists, '/exists')
myapi.add_resource(Search, '/search')
myapi.add_resource(Roles, '/roles')
