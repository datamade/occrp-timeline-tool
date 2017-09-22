import os
import unittest
import tempfile

from occrp.models import Story, Event, Person, Organization, Source, events_stories
from occrp.forms import StoryForm, EventForm

def test_story_form(db_session, client):
    """ Tests that the story form on the index page creates a story"""
    form = {'title': 'Real big news story'}

    client.post('/', data=form)
    story = db_session.query(Story).filter(Story.title=='Real big news story').first() 
    rv = client.get('/'.format(story.id))

    assert story.title == 'Real big news story'
    assert 'Real big news story' in rv.data.decode('utf8')


def test_event_form(db_session, client, story):
    """Tests that the event form on the story detail page creates an event"""
    form = {'description': 'Significant event'}
    client.post('/story/{}'.format(story.id), 
                data=form)
    rv = client.get('/story/{}'.format(story.id))
    event = db_session.query(Event).filter(Event.description == 'Significant event').first()
    associated_event = db_session.query(events_stories).filter(Event.description=='Significant event', Story.title=='Real big news story').filter(Story.title=='Real big news story').first()

    assert event.description == 'Significant event'
    assert "Nicely done! You've added a new event and its related data." in rv.data.decode('utf8')
    assert associated_event != None


def test_event_form_validate(db_session, client, story, event):
    """
    Tests that the event form validates for unique descriptions.
    Completes the form with an event description that already resides in the database: the form does not create a new event.
    """
    form = {'description': event.description}
    client.post('/story/{}'.format(story.id), 
                data=form)

    events = db_session.query(Event).all()

    assert len(events) == 1


def test_event_facets(db_session, client, story):
    """Tests that the event form creates instances of a person, organization, and source"""
    form = {'description': 'Significant event', 
            'person_name': 'Person of interest',
            'organization': 'Organization involved',
            'source_label': 'Source of the event'}

    client.post('/story/{}'.format(story.id), 
                data=form)
    person = db_session.query(Person).filter(Person.name == 'Person of interest').first()
    organization = db_session.query(Organization).filter(Organization.name == 'Organization involved').first()
    source = db_session.query(Source).filter(Source.label == 'Source of the event').first()

    assert person != None
    assert organization != None
    assert source != None
