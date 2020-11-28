import os.path
from .models import Units

def filter_year(year):
    result=Units.query.filter_by(year=year)
    return result
def filter_year_and_semester(year,semester):
    result=Units.query.filter_by(year=year,semester=semester)
    return result
    
def filter_semester(semester):
    result=Units.query.filter_by(semester=semester)
    return result
    
def filter_extension(data,ext):
    result=[]
    for item in data:
        if os.path.splitext(item.name)[-1]==ext:
            result.append(item)
    return result