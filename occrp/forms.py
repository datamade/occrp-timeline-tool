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
    source_label = StringField('source_label')
    person_name = StringField('person_name') # Should allow for multiple inputs
    organization = StringField('organization') # Should allow for multiple inputs

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
