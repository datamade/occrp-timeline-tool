import pytz
from datetime import datetime, timedelta
import json
from sqlalchemy import create_engine
from collections import OrderedDict

from flask import Blueprint, render_template, redirect, url_for, flash, request, make_response

from .models import * 
from .forms import StoryForm, EventForm
from .database import db
from .app_config import TIME_ZONE, DB_CONN
from .utils import parseDateAccuracy, get_or_create, autocomplete_results

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
    select_facet = request.args.get('facet', None)
    type_facet = request.args.get('type', 'Organizations')
    sort_order = request.args.get('sort', 'desc')
    order_by = request.args.get('order_by', 'start_date')

    toggle_order = 'asc'
    if sort_order.lower() == 'asc':
        toggle_order = 'desc'

    if form.validate_on_submit():
        description = form.data['description']
        event_type = form.data['event_type']
        significance = form.data['significance']
        start_date = form.data['start_date']
        end_date = form.data['end_date']
        source_list = request.form.getlist('source_label')
        organization_list = request.form.getlist('organization')
        person_name_list = request.form.getlist('person_name')

        event, event_created = get_or_create(Event, 
                          description=description.strip())

        if event_created:
            # Add event
            db.session.add(event)

            if event_type:
                event_type_obj, event_type_created = get_or_create(EventType,
                                      name=event_type.strip())
                event.event_type_id = event_type_obj.id

            if significance:
                event.significance = significance.strip()

            if start_date:
                start_date, start_date_accuracy = parseDateAccuracy(start_date.strip())
                event.start_date = start_date
                event.start_date_accuracy = start_date_accuracy

            if end_date:
                end_date, end_date_accuracy = parseDateAccuracy(end_date.strip())
                event.end_date = end_date
                event.end_date_accuracy = end_date_accuracy
        
            # Create and add people, source, and organizations
            if not all('' == p for p in person_name_list):
                for person_name in person_name_list:
                    person, person_created = get_or_create(Person,
                                      name=person_name.strip())
                    event.people.append(person)

            if not all('' == s for s in source_list):
                for source_label in source_list:
                    source, source_created = get_or_create(Source,
                                            label=source_label.strip())
                    event.sources.append(source)
            
            if not all('' == o for o in organization_list):
                for organization in organization_list:
                    org, org_created = get_or_create(Organization,
                                        name=organization.strip())
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
            form.description.errors.append('An event with this description already exists')
      
    
    people_facets = get_facets(entity_type='person', 
                               field='name', 
                               join_table='people_events', 
                               story_id=story.id, 
                               query=query,
                               select_facet=select_facet)  
    
    organization_facets = get_facets(entity_type='organization', 
                                    field='name', 
                                    join_table='events_organizations', 
                                    story_id=story.id, 
                                    query=query,
                                    select_facet=select_facet) 
    
    source_facets = get_facets(entity_type='source', 
                              field='label', 
                              join_table='events_sources', 
                              story_id=story.id, 
                              query=query,
                              select_facet=select_facet)

    facets = {
        'People': people_facets,
        'Organizations': organization_facets,
        'Sources': source_facets,
    }

    facets = OrderedDict(sorted(facets.items()))

    events = get_query_results(story_id=story_id, 
                               query=query, 
                               select_facet=select_facet, 
                               order_by=order_by, 
                               sort_order=sort_order)
        
    return render_template('story.html', 
                          form=form,
                          story=story,
                          facets=facets,
                          events=events,
                          query=query,
                          select_facet=select_facet,
                          type_facet=type_facet,
                          order_by=order_by,
                          toggle_order=toggle_order)


@views.route('/about')
def about():
    return render_template('about.html')


@views.route('/eventtype-autocomplete/')
def eventtype_autocomplete():
    term = request.args['q']

    return autocomplete_results(EventType.name, term)


@views.route('/person-autocomplete/')
def person_autocomplete():
    term = request.args['q']

    return autocomplete_results(Person.name, term)


@views.route('/organization-autocomplete/')
def organization_autocomplete():
    term = request.args['q']

    return autocomplete_results(Organization.name, term)


@views.route('/source-autocomplete/')
def source_autocomplete():
    term = request.args['q']

    return autocomplete_results(Source.label, term)


def get_facets(**kwargs):
    facets_query = '''
        SELECT TRIM({entity_type}.{field}) as facet, array_length(array_agg(distinct event.id), 1) as facet_count
        FROM story
        LEFT JOIN events_stories ON story.id = events_stories.story_id 
        LEFT JOIN event ON events_stories.event_id = event.id 
        LEFT JOIN people_events ON event.id = people_events.event_id
        LEFT JOIN person ON people_events.person_id = person.id
        LEFT JOIN events_organizations ON event.id = events_organizations.event_id       
        LEFT JOIN organization ON events_organizations.organization_id = organization.id 
        LEFT JOIN events_sources ON event.id = events_sources.event_id       
        LEFT JOIN source ON events_sources.source_id = source.id 
        WHERE story.id={story_id}
    '''.format(entity_type=kwargs['entity_type'],
                field=kwargs['field'],  
                story_id=kwargs['story_id'])

    if kwargs['query']:
        facets_query += '''
            AND plainto_tsquery('english', '{query}') @@ to_tsvector(event.description || ' ' || event.significance || ' ' || coalesce(source.label, '') || ' ' || coalesce(person.name, '') || ' ' || coalesce(person.email, '') || ' ' || coalesce(organization.name, ''))
            '''.format(query=kwargs['query'])

    if kwargs['select_facet']:
        facets_query += '''
            AND (person.name='{select_facet}' or organization.name='{select_facet}' or source.label='{select_facet}')
            '''.format(select_facet=kwargs['select_facet'])

    facets_query += '''
        GROUP BY {entity_type}.{field}
        '''.format(entity_type=kwargs['entity_type'], field=kwargs['field'])

    facets = engine.execute(facets_query).fetchall()
    facets = [dict(f) for f in facets if f[0] != None]
    return facets


def get_query_results(**kwargs):
    results_query = '''
        SELECT DISTINCT e.start_date, e.end_date, e.start_date_accuracy, e.end_date_accuracy, e.description, e.significance 
        FROM event as e
        LEFT JOIN events_stories ON e.id = events_stories.event_id 
        LEFT JOIN story ON events_stories.story_id = story.id
        LEFT JOIN people_events ON e.id = people_events.event_id
        LEFT JOIN person ON people_events.person_id = person.id
        LEFT JOIN events_organizations ON e.id = events_organizations.event_id       
        LEFT JOIN organization ON events_organizations.organization_id = organization.id 
        LEFT JOIN events_sources ON e.id = events_sources.event_id       
        LEFT JOIN source ON events_sources.source_id = source.id 
        WHERE story_id={story_id}
        '''.format(story_id=kwargs['story_id'])

    if kwargs['query']:
        results_query += '''
            AND plainto_tsquery('english', '{query}') @@ to_tsvector(e.description || ' ' || e.significance || ' ' || coalesce(source.label, '') || ' ' || coalesce(person.name, '') || ' ' || coalesce(person.email, '') || ' ' || coalesce(organization.name, ''))
            '''.format(query=kwargs['query'])

    if kwargs['select_facet']:
        results_query += '''
        AND (person.name='{select_facet}' or organization.name='{select_facet}' or source.label='{select_facet}')
        '''.format(select_facet=kwargs['select_facet'])

    results_query += '''
        ORDER BY {order_by} {sort_order}
        '''.format(order_by=kwargs['order_by'],
                   sort_order=kwargs['sort_order'])

    return engine.execute(results_query).fetchall()

