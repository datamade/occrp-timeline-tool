import sqlalchemy as sa

from flask_wtf import FlaskForm

from wtforms import StringField, DateField
from wtforms.validators import DataRequired

from .utils import parseDateAccuracy

class StoryForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])


class EventForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    start_date = StringField('start_date')
    end_date = StringField('end_date')
    description = StringField('description')
    significance = StringField('significance')
    person_name = StringField('person_name')
    source_label = StringField('source_label')
    organization = StringField('organization')

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        
        if self.start_date.data and self.end_date.data:
            start_date, _ = parseDateAccuracy(self.start_date.data)
            end_date, _ = parseDateAccuracy(self.end_date.data)

            if end_date < start_date:
                self.end_date.errors.append('End date is before the start date')

        if self.errors:
            return False

        return True
