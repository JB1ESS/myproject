from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

class ApartSearchForm(FlaskForm):
    #keyword = StringField('검색', validators=[DataRequired()])
    form_bjd = StringField('법정동', validators=[DataRequired()])
    form_area = StringField('전용면적', validators=[DataRequired()])
    form_apt = StringField('아파트', validators=[DataRequired()])