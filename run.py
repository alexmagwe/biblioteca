from app import create_app,db
import unittest
from app.models import Users,Courses,Permissions,Units,Notes,AdminsList
from flask_migrate import Migrate,upgrade


app=create_app()
migrate=Migrate(app,db)

@app.shell_context_processor
def make_shell_context():
    return {'db':db,'Users':Users,'Courses':Courses,'AdminsList':AdminsList,'Permissions':Permissions,'Notes':Notes,'Units':Units}
@app.cli.command()
def deploy():
    upgrade()

    
if __name__=='__main__':
    app.run()