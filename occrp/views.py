import pytz
from datetime import datetime, timedelta

from flask import Blueprint, render_template, redirect, url_for, flash
from flask import request

from .models import Story, Person
from .forms import StoryForm, PersonForm
from .database import db
from .app_config import TIME_ZONE

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
        db.session.add(story)
        db.session.commit()

        if created:
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
    form = PersonForm()
    story = Story.query.get(story_id)

    if form.validate_on_submit():
        
        person = Person(name=form.data['name'],
                        mail=form.data['email'])
        db.session.add(person)
        db.session.commit()

        flash('Person {} saved!'.format(person.name))
    
    return render_template('story.html', 
                          form=form,
                          story=story)


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