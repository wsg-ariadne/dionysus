from database import create_app, db
from flask import url_for
from flask_cors import CORS
from middleware.logger import LoggingMiddleware
from routes import install_routes
from sqlalchemy import exc
import configparser


# Read config from dionysus.conf
try:
    config = configparser.ConfigParser()
    config.read('dionysus.conf')

    # Save database connection details
    db_host = config['database']['host']
    db_port = config['database']['port']
    db_user = config['database']['user']
    db_pass = config['database']['pass']
    db_name = config['database']['name']

    # Save app configs
    debug = config['dionysus'].getboolean('debug')
    enable_middleware = config['dionysus'].getboolean('enable_logger_middleware')
    cors_origins = config['dionysus']['cors_origins']
    api_prefix = config['dionysus']['api_prefix']
except FileNotFoundError:
    print("Config file not found")
    exit(1)
except KeyError as e:
    print("Config file is missing a key: " + str(e))
    exit(1)


# Create Flask app and SQLAlchemy instance
app = create_app(__name__, database_uri=f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}')
app.app_context().push()
db.create_all()

# Enable CORS
cors = CORS(app, resources={
    rf'{api_prefix}/*': {
        'origins': cors_origins,
        'allow_headers': ['authorization', 'content-type']
    }
})

# Add routes
app.config['API_URL_PREFIX'] = api_prefix
install_routes(app)
if debug:
    def has_no_empty_params(rule):
        defaults = rule.defaults if rule.defaults is not None else ()
        arguments = rule.arguments if rule.arguments is not None else ()
        return len(defaults) >= len(arguments)

    @app.route("/site-map")
    def site_map():
        links = []
        for rule in app.url_map.iter_rules():
            # Filter out rules we can't navigate to in a browser
            # and rules that require parameters
            if "GET" in rule.methods and has_no_empty_params(rule):
                url = url_for(rule.endpoint, **(rule.defaults or {}))
                links.append((url, rule.endpoint))
        # links is now a list of url, endpoint tuples
        return str(links)


# Error handler
@app.errorhandler(exc.SQLAlchemyError)
def sqlalchemy_error(error):
    db.session.rollback()
    return {
        'success': False,
        'error': 'Internal server error: ' + str(error)
    }, 500


# Start Flask app
if __name__ == '__main__':
    if enable_middleware:
        app.wsgi_app = LoggingMiddleware(app.wsgi_app)
    app.run(debug=debug)
