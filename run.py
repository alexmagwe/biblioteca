from app import create_app
from app.models import Users,Courses,AdminsList,Permissions,Notes,Units


app=create_app('development')
@app.context_processor
def inject_models():
    return {'Users':Users,'Courses':Courses,'AdminsList':AdminsList,'Permissions':Permissions,'Notes':Notes,'Units':Units}

if __name__=='__main__':
    app.run()
