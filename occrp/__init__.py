from flask import Flask
import urllib

from flask_sqlalchemy import SQLAlchemy

from .views import views
from .database import db

def create_app(name=__name__, settings_override={}):
    app = Flask(name)
    config = '{0}.app_config'.format(__name__)
    app.config.from_object(config)
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['DB_CONN'] 
    
    for k,v in settings_override.items():
        app.config[k] = v

    db.init_app(app)

    app.register_blueprint(views)
    
    @app.template_filter('format_date')
    def format_date(s, fmt='%Y-%m-%d %-I:%M%p'):
        if s:
            return s.strftime(fmt)

        return None

    @app.template_filter('query_transform')
    def query_transform(request, **kwargs):
        query = request.args.get('q', None)
        select_facet = request.args.get('facet', None)
        type_facet = request.args.get('type', None)

        request_args = {}
        if query:
            request_args['q'] = query
        if select_facet:
            request_args['facet'] = select_facet
        if type_facet:
            request_args['type'] = type_facet
        for k,v in kwargs.items():
            request_args[k] = v
        encoded = urllib.parse.urlencode(request_args)

        return encoded

    @app.template_filter('get_sort_icon')
    def get_sort_icon(s):
        if 'desc' in str(s.lower()):
            return ' <i class="fa fa-sort-amount-asc"> </i>'
        return ' <i class="fa fa-sort-amount-desc"> </i>'
    
    return app
