# occrp-timeline-tool

The OCCRP Timeline Tool helps reporters capture, organize, and view sequences of events and how they related to networks of organizations, people, and sources. 

## Get started
To get started, run the following commands in your shell:

```bash
# Clone the repo
git clone git@github.com:datamade/occrp-timeline-tool.git
cd occrp-timeline-tool
```

We recommend using [virtualenv](https://virtualenv.readthedocs.io/en/latest/)
and
[virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/install.html)
for working in a virtualized development environment. [Learn about how to set up
virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

Then, do the following in your bash profile:

```bash
mkvirtualenv occrp
pip install -r requirements.txt
```

At this point, you successfully installed several packages onto your virtual environment. If you want to see what lives inside the "occrp" virtualenv, then simply type:

```bash
pip freeze
```

And remember, whenever you want to use this virtual environment (and all its installed modules), run:

```bash
workon occrp
```

## Setup

We use DataMade's [Flask App Template](https://github.com/datamade/flask_app_template) as a blueprint for the site framework.

Copy the `app_config.py.example`:

```bash
cp app_config.py.example
app_config.py
```

Update these variables:

```bash
DB_USER = ''
DB_PW = ''
DB_HOST = ''
DB_PORT = ''
DB_NAME = 'occrp'
```

The DB_USER and DB_PW most likely will remain an empty string, for local development. Likewise, DB_HOST might be "localhost," and DB_PORT may be "5432."

Then, create your database, and run our custom script to generate tables:

```bash
createdb occrp
python init_db.py
```

We use [Alembic](http://alembic.zzzcomputing.com/en/latest/index.html) and SQLAlchemy to track migrations and to update the database, whenever changes in the models occur. To run the migrations:

You might make modifications to the model(s). If so, create a new migration:

```bash
alembic revision --autogenerate -m "Add first_name first to Person model"
```

Then, run the migration: 

```bash
alembic upgrade head
```

## Team

* Regina Compton
* Eric Van Zanten

