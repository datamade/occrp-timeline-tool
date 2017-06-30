import sqlalchemy as sa

from flask_wtf import FlaskForm

from wtforms import StringField, DateTimeField
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
    start_date = DateTimeField('start_date')
    end_date = DateTimeField('end_date')
    description = StringField('description')
    significance = StringField('significance')

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        if self.errors:
            return False

        return True
