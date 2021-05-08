from . import myapi
from .resources import AddUnit,AddCourse,AddMyCourse,CourseDetails,CourseNotes,AllCourses,AllNotes,AddNotes,AllUnits,GetUnits,UnitNotes,Exists,Search

myapi.add_resource(AllCourses,'/courses/all')
myapi.add_resource(CourseNotes,'/course/notes/all')
myapi.add_resource(AddCourse,'/add/course')
myapi.add_resource(CourseDetails,'/course/details')
myapi.add_resource(GetUnits,'/course/units')
myapi.add_resource(AddNotes,'/add/notes')
myapi.add_resource(AddMyCourse,'/add/mycourse')
myapi.add_resource(AllNotes,'/notes/all')
myapi.add_resource(UnitNotes,'/unit/notes/all')
myapi.add_resource(AllUnits,'/units/all')
myapi.add_resource(AddUnit,'/add/unit')
myapi.add_resource(Exists,'/exists')
myapi.add_resource(Search,'/search')
