import pytz
from datetime import datetime, timedelta
from sqlalchemy import create_engine

from flask import Blueprint, render_template, redirect, url_for, flash, request

from .models import * 
from .forms import StoryForm, EventForm
from .database import db
from .app_config import TIME_ZONE, DB_CONN
from .utils import parseDateAccuracy, get_or_create

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
    query = request.args.get('q', None)
    sort_order = request.args.get('sort', 'desc')
    order_by = request.args.get('order_by', 'start_date')

    toggle_order = 'asc'
    if sort_order.lower() == 'asc':
        toggle_order = 'desc'

    if form.validate_on_submit():
        title = form.data['title']
        start_date = form.data['start_date']
        end_date = form.data['end_date']
        description = form.data['description']
        significance = form.data['significance']
        person_name = form.data['person_name']
        source_label = form.data['source_label']
        organization = form.data['organization']
        
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

            if source_label:
                source, source_created = get_or_create(Source,
                                        label=source_label)
                event.sources.append(source)
            
            if organization:
                org, org_created = get_or_create(Organization,
                                    name=organization)
                event.organizations.append(org)
                
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
      
    
    people_facets = get_facets(entity_type='person', 
                               field='name', 
                               join_table='people_events', 
                               story_id=story.id, 
                               query=query)  
    
    organization_facets = get_facets(entity_type='organization', 
                                    field='name', 
                                    join_table='events_organizations', 
                                    story_id=story.id, 
                                    query=query) 
    
    source_facets = get_facets(entity_type='source', 
                              field='label', 
                              join_table='events_sources', 
                              story_id=story.id, 
                              query=query)

    facets = {
        'People': people_facets,
        'Organizations': organization_facets,
        'Sources': source_facets,
    }

    events = get_query_results(story_id, query, order_by, sort_order)
        
    return render_template('story.html', 
                          form=form,
                          story=story,
                          facets=facets,
                          events=events,
                          query=query,
                          order_by=order_by,
                          toggle_order=toggle_order
                          )


@views.route('/about')
def about():
    return render_template('about.html')


def get_facets(**kwargs):
    facets_query = '''
        SELECT trim({entity_type}.{field}) as facet, count({entity_type}.id) as facet_count 
        FROM story
        JOIN events_stories ON story.id = events_stories.story_id 
        JOIN event ON events_stories.event_id = event.id 
        JOIN {join_table} ON event.id = {join_table}.event_id 
        JOIN {entity_type} ON {join_table}.{entity_type}_id = {entity_type}.id 
        WHERE story.id={story_id}
        AND plainto_tsquery('english', '{query}') @@ to_tsvector(event.title || ' ' || event.description || ' ' || event.significance)
        GROUP BY {entity_type}.{field}
    '''.format(entity_type=kwargs['entity_type'],
                field=kwargs['field'],  
                join_table=kwargs['join_table'], 
                story_id=kwargs['story_id'],
                query=kwargs['query'])

    facets = engine.execute(facets_query).fetchall()
    facets = [dict(f) for f in facets]
    return facets


def get_query_results(story_id, query, order_by, sort_order):
    results_query = '''
        SELECT e.title, e.start_date, e.end_date, e.start_date_accuracy, e.end_date_accuracy, e.description, e.significance 
        FROM event as e
        JOIN events_stories ON e.id = events_stories.event_id 
        JOIN story ON events_stories.story_id = story.id
        WHERE story_id={story_id}
        '''.format(story_id=story_id)

    if query:
        results_query += '''
            AND plainto_tsquery('english', '{query}') @@ to_tsvector(e.title || ' ' || e.description || ' ' || e.significance)
            '''.format(query=query)

    results_query += '''
        ORDER BY {order_by} {sort_order}
        '''.format(order_by=order_by,
                   sort_order=sort_order)

    return engine.execute(results_query).fetchall()
