from app import create_app
import click,sys
from app.models import Users,Courses,AdminsList,Permissions,Notes,Units
import os
if os.environ.get('ENV')=='production':
    app=create_app('production')
else:
    print('creating app in dev mode')
    app=create_app('development')
#injects models data directly into templates
@app.context_processor
def inject_models():
    return {'Users':Users,'Courses':Courses,'AdminsList':AdminsList,'Permissions':Permissions,'Notes':Notes,'Units':Units}


COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()
# ...
@app.cli.command()
@click.option('--coverage/--no-coverage', default=False,
help='Run tests under code coverage.')
def test(coverage):
    #Run the unit tests
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()

if __name__=='__main__':
    app.run()
