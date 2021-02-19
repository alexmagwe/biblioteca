import os
from dotenv import load_dotenv
rootpath=os.path.abspath(os.path.dirname(__file__))
class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    SQL_ALCHEMY_COMMIT_ON_TEARDOWN=True   
    FLASK_APP=os.environ.get('FLASK_APP') 
    GOOGLE_CLIENT_ID=os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET=os.environ.get('GOOGLE_CLIENT_SECRET')
    GOOGLE_DISCOVERY_URL="https://accounts.google.com/.well-known/openid-configuration"
class Development(Config):
    envpath=os.path.abspath(os.path.dirname(__package__))
    load_dotenv(os.path.join(envpath,'.env'))
    SECRET_KEY=os.getenv('SECRET_KEY')
    DB_SERVER='localhost'
    MAIL_SERVER='smtp.mailtrap.io'
    MAIL_PORT=2525
    ADMINS=os.environ.get('ADMINS')
    MAIL_USE_TLS=True
    DEBUG=True
    MAIL_USE_SSL=False
    MAIL_USERNAME= '18046de32e56fe'
    MAIL_PASSWORD= 'a0ad48ed8fb0a0'
    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL')
class Production(Config):
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL')
    MAIL_USE_TLS=True
    FLASK_ENV='production'
    MAIL_SERVER='smtp.mailtrap.io'
    MAIL_PORT=2525
    SECRET_KEY=os.environ.get('SECRET_KEY')
    MAIL_USERNAME= '18046de32e56fe'
    MAIL_PASSWORD= 'a0ad48ed8fb0a0'
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
  
configs={
    'development':Development,
    'production':Production
}
