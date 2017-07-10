import pytz
from datetime import datetime, timedelta
import json

from flask import Blueprint, render_template, redirect, url_for, flash,\
    make_response
from flask import request

import sqlalchemy as sa

from .models import Story, Event, Person, Organization
from .forms import StoryForm, EventForm
from .database import db
from .app_config import TIME_ZONE
from .utils import parseDateAccuracy

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def index():
    form = StoryForm()
    stories = Story.query.all()
    message = request.args.get('message')

    if form.validate_on_submit():
        title = form.data['title']
        created_at = datetime.now(TIME_ZONE)

        story, created = get_or_create(Story,
                          title=title,
                          created_at=created_at)

        if created:
            db.session.add(story)
            db.session.commit()
            message = 'Nicely done! You\'ve added a new story.'
            return redirect(url_for('views.index', message=message))
        else:
            form.title.errors.append('A story with this title already exists')

    return render_template('index.html',
                          form=form,
                          message=message,
                          stories=stories)


@views.route('/story/<story_id>', methods=['GET', 'POST'])
def story(story_id):
    form = EventForm()
    story = Story.query.get(story_id)

    if form.validate_on_submit():
        title = form.data['title']
        start_date = form.data['start_date']
        end_date = form.data['end_date']
        description = form.data['description']
        significance = form.data['significance']
        person_name = form.data['person_name']
        
        if start_date:
            start_date, start_date_accuracy = parseDateAccuracy(start_date)
        
        if end_date:
            end_date, end_date_accuracy = parseDateAccuracy(end_date)
        
        event, event_created = get_or_create(Event, 
                          title=title, 
                          start_date=start_date,
                          start_date_accuracy=start_date_accuracy,
                          end_date=end_date,
                          end_date_accuracy=end_date_accuracy,
                          description=description,
                          significance=significance)


        if event_created:
            # Add event
            db.session.add(event)

            # Create and add person
            if person_name:
                person, person_created = get_or_create(Person,
                                  name=person_name)

                event.people.append(person)

            # Update story
            story.events.append(event)
            db.session.add(story)
            story.updated_at = datetime.now(TIME_ZONE)
            db.session.commit()

            message = 'Nicely done! You\'ve added a new event and its related data.'
            return redirect(url_for('views.story', story_id=story.id, message=message))
        else:
            form.title.errors.append('An event with this title already exists')


    return render_template('story.html',
                          form=form,
                          story=story)


@views.route('/people-search/')
def people_search():
    term = request.args['term']

    where = Person.name.ilike('%{}%'.format(term))

    people = db.session.query(sa.distinct(Person.name))\
                       .filter(where)\
                       .order_by(Person.name)

    people = [{'person': c[0]} for c in people.all()]

    response = make_response(json.dumps(people))

    response.headers['Content-Type'] = 'application/json'

    return response


@views.route('/organization-search/')
def organizations_search():
    term = request.args['term']

    where = Organization.name.ilike('%{}%'.format(term))

    organizations = db.session.query(sa.distinct(Organization.name))\
                       .filter(where)\
                       .order_by(Organization.name)

    organizations = [{'person': c[0]} for c in organizations.all()]

    response = make_response(json.dumps(organizations))

    response.headers['Content-Type'] = 'application/json'

    return response

@views.route('/about')
def about():
    return render_template('about.html')


def get_or_create(model, **kwargs):
    instance = db.session.query(model).filter_by(**kwargs).first()
    if instance:
        return (instance, False)
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return (instance, True)
