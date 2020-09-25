from . import myapi
from .resources import AddUnit,AddCourse,AddMyCourse,CourseDetails,CourseNotes,AllCourses,AllNotes,Upload,AllUnits,GetUnits,UnitNotes

myapi.add_resource(AllCourses,'/courses/all')
myapi.add_resource(CourseNotes,'/course/notes')
myapi.add_resource(AddCourse,'/add/course')
myapi.add_resource(CourseDetails,'/course/details')
myapi.add_resource(GetUnits,'/course/units')
myapi.add_resource(Upload,'/upload')
myapi.add_resource(AddMyCourse,'/add/mycourse')
myapi.add_resource(AllNotes,'/notes/all')
myapi.add_resource(UnitNotes,'/notes/all')
myapi.add_resource(AllUnits,'/units/all')
myapi.add_resource(AddUnit,'/add/units')

