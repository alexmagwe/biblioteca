from app import db
import os
from run import app
from flask_migrate import Migrate,MigrateCommand
from flask_script import Shell,Manager
from flask import current_app
from app.models import Users,Courses,Permissions,Units,Notes,AdminsList
manager=Manager(app)
@app.shell_context_processor
def make_shell_context():
    return {'db':db,'Users':Users,'Courses':Courses,'AdminsList':AdminsList,'Permissions':Permissions,'Notes':Notes,'Units':Units}
manager.add_command('shell',Shell(make_context=make_shell_context))
manager.add_command('db',MigrateCommand)

@app.context_processor
def inject_permissions():
    return dict(Permissions=Permissions)
if __name__=='__main__':
    manager.run()

