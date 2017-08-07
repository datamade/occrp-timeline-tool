import pytz
from datetime import datetime, timedelta
from sqlalchemy import create_engine

from flask import Blueprint, render_template, redirect, url_for, flash, request

from .models import * 
from .forms import StoryForm, EventForm
from .database import db
from .app_config import TIME_ZONE, DB_CONN
from .utils import parseDateAccuracy

views = Blueprint('views', __name__)
engine = create_engine(DB_CONN, convert_unicode=True)

@views.route('/', methods=['GET', 'POST'])
def index():
    form = StoryForm()
    stories = Story.query.all()

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
            flash(message)
            return redirect(url_for('views.index'))
        else:
            form.title.errors.append('A story with this title already exists')

    return render_template('index.html', 
                          form=form, 
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
        else:
            start_date = None
            start_date_accuracy = None

        if end_date:
            end_date, end_date_accuracy = parseDateAccuracy(end_date)
        else:
            end_date = None
            end_date_accuracy = None
        
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
            flash(message)
            return redirect(url_for('views.story', story_id=story.id))
        else:
            form.title.errors.append('An event with this title already exists')
      
    
    people_facets_query = '''
        SELECT trim(person.name) as facet, count(person.id) as facet_count 
        FROM story
        JOIN events_stories ON story.id = events_stories.story_id 
        JOIN event ON events_stories.event_id = event.id 
        JOIN people_events ON event.id = people_events.event_id 
        JOIN person ON people_events.person_id = person.id 
        WHERE story.id={}
        GROUP BY person.name
    '''.format(story_id)

    people_facets = engine.execute(people_facets_query).fetchall()
    people_facets = [dict(p) for p in people_facets]

    organizations_facets_query = '''
        SELECT trim(organization.name) as facet, count(organization.id) as facet_count 
        FROM story
        JOIN events_stories ON story.id = events_stories.story_id 
        JOIN event ON events_stories.event_id = event.id 
        JOIN events_organizations ON event.id = events_organizations.event_id 
        JOIN organization ON events_organizations.organization_id = organization.id 
        WHERE story.id={}
        GROUP BY organization.name
    '''.format(story_id)
    
    organization_facets = engine.execute(organizations_facets_query).fetchall()
    organization_facets = [dict(o) for o in organization_facets]

    sources_facets_query = '''
        SELECT trim(source.label) as facet, count(source.id) as facet_count 
        FROM story
        JOIN events_stories ON story.id = events_stories.story_id 
        JOIN event ON events_stories.event_id = event.id 
        JOIN events_sources ON event.id = events_sources.event_id 
        JOIN source ON events_sources.source_id = source.id 
        WHERE story.id={}
        GROUP BY source.label
    '''.format(story_id)
    
    source_facets = engine.execute(sources_facets_query).fetchall()
    source_facets = [dict(s) for s in source_facets]

    facets = {
        'People': people_facets,
        'Organizations': organization_facets,
        'Sources': source_facets,
    }

    return render_template('story.html', 
                          form=form,
                          story=story,
                          facets=facets,
                          )


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
