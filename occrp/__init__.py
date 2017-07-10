from flask import Flask

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
    
    return app
