import os

import pytest

from pytest_postgresql.factories import (
    init_postgresql_database, drop_postgresql_database, get_config,
)

import psycopg2

from occrp import create_app
from occrp.database import db as _db
from occrp.models import Story, Event
from occrp.app_config import DB_OPTS, DB_CONN


@pytest.fixture(scope='session')
def database(request):
    pg_host = DB_OPTS.get("host")
    pg_port = DB_OPTS.get("port")
    pg_user = DB_OPTS.get("user")
    pg_db = DB_OPTS.get("name", "tests")
    
    if 'test' not in pg_db:
        pg_db = '{}_test'.format(pg_db)

    # Create our Database.
    try:
        init_postgresql_database(pg_user, pg_host, pg_port, pg_db)
    except psycopg2.ProgrammingError as e:
        if 'permission denied' in str(e):
            pg_user = 'postgres'
            init_postgresql_database(pg_user, pg_host, pg_port, pg_db)
        else:
            raise e


    # Ensure our database gets deleted.
    @request.addfinalizer
    def drop_database():
        drop_postgresql_database(pg_user, pg_host, pg_port, pg_db, 9.6)


@pytest.fixture(scope='session')
def app(request, database):
    """Session-wide test `Flask` application."""
    settings_override = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': DB_CONN,
        'WTF_CSRF_ENABLED': False,
    }
    app = create_app('occrp', settings_override)

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='session')
def db(app, request):
    
    _db.app = app
    _db.create_all()
    
    def teardown():
        _db.drop_all()
    
    request.addfinalizer(teardown)
    
    return _db


@pytest.fixture(scope='function')
def db_session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session


@pytest.fixture(scope='function')
def story(db, request):
    """Creates a new instance of a story."""
    story = Story(title='Real big news story')
    db.session.add(story)
    db.session.commit()

    def teardown():
        db.session.delete(story)
    
    request.addfinalizer(teardown)
    return story


@pytest.fixture(scope='function')
def event(db, request):
    """Creates a new instance of an event."""
    event = Event(description='Juicy meaningful event')
    db.session.add(event)
    db.session.commit()

    def teardown():
        db.session.delete(event)
    
    request.addfinalizer(teardown)
    return event
