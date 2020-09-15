from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import MetaData
from flask_migrate import Migrate,MigrateCommand
from flask_mail import Mail 
import os
from flask_admin import Admin
# from flask_mongoengine import MongoEngine
from flask_sqlalchemy import SQLAlchemy
from notes01.config import configs
from flask_bootstrap import Bootstrap
meta = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
      })

db=SQLAlchemy()
mail=Mail()
bootstrap=Bootstrap()
admin=Admin(name='Admin')
login_manager=LoginManager()
login_manager.login_view='auth.login'
login_manager.login_message_category='info'
migrate=Migrate()

def create_app():
    app=Flask(__name__)
    app.config.from_object(configs['production'])
    mail.init_app(app)
    login_manager.init_app(app)
    admin.init_app(app)
    migrate.init_app(app,db,render_as_batch=True)
    db.init_app(app)
    bootstrap.init_app(app)
    from notes01.app.api import api
    app.register_blueprint(api) 
    from notes01.app.auth import auth
    app.register_blueprint(auth,url_prefix='/auth')
    return app
            
def getuploadpath():
  path=os.path.join(os.path.dirname(__file__),'static/toupload')
  return path