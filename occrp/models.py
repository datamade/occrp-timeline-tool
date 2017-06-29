import sqlalchemy as sa
from sqlalchemy.orm import backref, relationship
from sqlalchemy import Integer, String, Boolean, DateTime, Column, Table, ForeignKey

from .database import db

people_organizations = Table('people_organizations', db.Model.metadata,
        Column('person_id', Integer(), ForeignKey('person.id')),
        Column('organization_id', Integer(), ForeignKey('organization.id')))

people_sources = Table('people_sources', db.Model.metadata,
        Column('person_id', Integer(), ForeignKey('person.id')),
        Column('source_id', Integer(), ForeignKey('source.id')))

people_events = Table('people_events', db.Model.metadata,
        Column('person_id', Integer(), ForeignKey('person.id')),
        Column('event_id', Integer(), ForeignKey('event.id')))

organizations_sources = Table('organizations_sources', db.Model.metadata,
        Column('organization_id', Integer(), ForeignKey('organization.id')),
        Column('source_id', Integer(), ForeignKey('source.id')))

events_sources = Table('events_sources', db.Model.metadata,
        Column('event_id', Integer(), ForeignKey('event.id')),
        Column('source_id', Integer(), ForeignKey('source.id')))

events_organizations = Table('events_organizations', db.Model.metadata,
        Column('event_id', Integer(), ForeignKey('event.id')),
        Column('organization_id', Integer(), ForeignKey('organization.id')))

events_stories = Table('events_stories', db.Model.metadata,
        Column('event_id', Integer(), ForeignKey('event.id')),
        Column('story_id', Integer(), ForeignKey('story.id')))

class Person(db.Model):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    
    def __repr__(self): # pragma: no cover
        return '<PersonModel %r>' % self.name

class Organization(db.Model):
    __tablename__ = 'organization'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    people = relationship('Person', secondary=people_organizations,
                            backref=backref('organizations', lazy='dynamic'))
    events = relationship('Event', secondary=events_organizations,
                            backref=backref('organizations', lazy='dynamic'))

class Source(db.Model):
    __tablename__ = 'source'
    id = Column(Integer, primary_key=True)
    label = Column(String, nullable=False, unique=True)
    people = relationship('Person', secondary=people_sources, 
                            backref=backref('sources', lazy='dynamic'))
    organizations = relationship('Organization', secondary=organizations_sources, 
                            backref=backref('sources', lazy='dynamic'))
    events = relationship('Event', secondary=events_sources,
                            backref=backref('sources', lazy='dynamic'))

class Event(db.Model):
    __tablename__ = 'event'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False, unique=True)
    start_date = Column(DateTime) 
    end_date = Column(DateTime)
    people = relationship('Person', secondary=people_events,
                            backref=backref('events', lazy='dynamic'))

class Story(db.Model):
    __tablename__ = 'story'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    events = relationship('Event', secondary=events_stories,
                            backref=backref('stories', lazy='dynamic'))