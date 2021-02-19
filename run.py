from app import create_app
from app.models import Users,Courses,AdminsList,Permissions,Notes,Units
import os
if os.environ.get('ENV')=='production':
    app=create_app('production')
else:
    app=create_app('development')
#injects models data directly into templates
@app.context_processor
def inject_models():
    return {'Users':Users,'Courses':Courses,'AdminsList':AdminsList,'Permissions':Permissions,'Notes':Notes,'Units':Units}

if __name__=='__main__':
    app.run()
