import os
rootpath=os.path.abspath(os.path.dirname(__file__))
class Config:
    DB_SERVER='localhost'
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    SQL_ALCHEMY_COMMIT_ON_TEARDOWN=True    
    GOOGLE_CLIENT_ID=os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET=os.environ.get('GOOGLE_CLIENT_SECRET')
    GOOGLE_DISCOVERY_URL="https://accounts.google.com/.well-known/openid-configuration"
class Development(Config):
    SECRET_KEY=os.environ.get('SECRET_KEY')
    DB_NAME=os.environ.get('DB_NAME')
    MAIL_SERVER='smtp.mailtrap.io'
    MAIL_PORT=2525
    ADMINS=os.environ.get('ADMINS')
    MAIL_USE_TLS=True
    DEBUG=True
    # GOOGLE_APPLICATION_CREDENTIALS=os.path.abspath('Notes-c108a1523ab3.json')
    MAIL_USE_SSL=False
    MAIL_USERNAME= '18046de32e56fe'
    MAIL_PASSWORD= 'a0ad48ed8fb0a0'
    SQLALCHEMY_DATABASE_URI='sqlite:///'+os.path.join(rootpath,DB_NAME+'.sqlite')
class Production(Config):
    #to be updated
    SECRET_KEY=os.environ.get('SECRET_KEY')
  
configs={
    'development':Development,
    'production':Production
}
