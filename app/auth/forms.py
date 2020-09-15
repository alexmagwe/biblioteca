from ..models import AdminsList,AdminsList
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired,Email,ValidationError

class AdminForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired(),Email()])
    submit=SubmitField('Invite')
    def validate_email(self,email):
        user=AdminsList.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('admin already exists')
        
            