from notes01.app import create_app,db
from flask_migrate import Migrate,MigrateCommand
from flask_script import Shell,Manager
from notes01.app.models import Users,Courses,Permissions,Units,Notes,Teachers,AdminsList
app=create_app()

manager=Manager(app)

@app.shell_context_processor
def make_shell_context():
    return {'db':db,'Users':Users,'Courses':Courses,'AdminsList':AdminsList,'Permissions':Permissions,'Notes':Notes,'Teachers':Teachers,'Units':Units}

manager.add_command('shell',shell_context=make_shell_context)
manager.add_command('db',MigrateCommand)

@app.context_processor
def inject_permissions():
    return dict(Permissions=Permissions)
if os.environ.get('FLASK_ENV')=='production':
    app.run()
else:   
    manager.run()

