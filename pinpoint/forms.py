from flask.ext.wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired

class cityForm(Form):
    city = StringField('city', validators=[DataRequired()])
