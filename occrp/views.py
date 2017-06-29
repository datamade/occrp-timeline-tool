from flask import Blueprint, render_template, redirect, url_for, flash

from .models import Story, Person
from .forms import StoryForm, PersonForm
from .database import db

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def index():
    form = StoryForm()

    if form.validate_on_submit():
      title = form.data['title']

      story = Story(title=title)
      db.session.add(story)
      db.session.commit()

    return render_template('index.html', form=form)


@views.route('/story/<story_id>', methods=['GET', 'POST'])
def story(story_id):
    form = PersonForm()

    if form.validate_on_submit():
        
        person = Person(name=form.data['name'],
                             email=form.data['email'])
        db.session.add(person)
        db.session.commit()

        flash('Person {} saved!'.format(person.name))
    
    return render_template('story.html', form=form)


@views.route('/about')
def about():
    return render_template('about.html')
