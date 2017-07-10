import sqlalchemy as sa

from flask_wtf import FlaskForm

from wtforms import StringField, DateField
from wtforms.validators import DataRequired


class StoryForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])


class EventForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    start_date = StringField('start_date')
    end_date = StringField('end_date')
    description = StringField('description')
    significance = StringField('significance')
    person_name = StringField('person_name')
