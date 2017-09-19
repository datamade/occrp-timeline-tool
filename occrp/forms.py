import sqlalchemy as sa

from flask_wtf import FlaskForm

from wtforms import StringField, DateField
from wtforms.validators import DataRequired

from .utils import parseDateAccuracy

class StoryForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])


# Upon data entry: we should trim all strings, as they get entered
class EventForm(FlaskForm):
    description = StringField('description', validators=[DataRequired()])
    start_date = StringField('start_date', filters=[lambda x: x or None])
    end_date = StringField('end_date', filters=[lambda x: x or None])
    significance = StringField('significance', filters=[lambda x: x or None])
    event_type = StringField('event_type', filters=[lambda x: x or None])
    location = StringField('location', filters=[lambda x: x or None])
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
