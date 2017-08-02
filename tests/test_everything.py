import os
import unittest
import tempfile

from occrp.models import Story

def test_story(db_session):
    story = Story(title='Real big news')

    db_session.add(story)
    db_session.commit()

    added_story = db_session.query(Story).filter(Story.title == 'Real big news').first()

    assert added_story.title == 'Real big news'
    
