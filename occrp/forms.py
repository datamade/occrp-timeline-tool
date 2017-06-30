import sqlalchemy as sa

from flask_wtf import FlaskForm

from wtforms import StringField, DateField
from wtforms.validators import DataRequired

from .models import Person
from .database import db


class StoryForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        if self.errors:
            return False

        return True


class EventForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    start_date = DateField('start_date')
    end_date = DateField('end_date')
    description = StringField('description')
    significance = StringField('significance')
    person_name = StringField('person_name')

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        if self.errors:
            return False

        return True
