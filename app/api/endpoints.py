from . import myapi
from .resources import AddUnit,AddCourse,AddMyCourse,CourseDetails,CourseNotes,AllCourses,AllNotes,Upload,AllUnits,GetUnits,UnitNotes

myapi.add_resource(AllCourses,'/courses')
myapi.add_resource(CourseNotes,'/course_notes')
myapi.add_resource(AddCourse,'/add_course')
myapi.add_resource(CourseDetails,'/course_details')
myapi.add_resource(GetUnits,'/course_units')
myapi.add_resource(Upload,'/upload')
myapi.add_resource(AddMyCourse,'/add_mycourse')
myapi.add_resource(AllNotes,'/all_notes')
myapi.add_resource(UnitNotes,'/unit_notes')
myapi.add_resource(AllUnits,'/all_units')
myapi.add_resource(AddUnit,'/add/unit')

