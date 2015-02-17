from flask import Flask


def create_app():
    app = Flask(__name__)

    # Configuration
    import mbspotify.default_config
    app.config.from_object(mbspotify.default_config)
    app.config.from_pyfile('config.py')

    # Logging
    from mbspotify import loggers
    loggers.init_loggers(app)

    # Blueprints
    from mbspotify.views import main_bp
    app.register_blueprint(main_bp)

    return app
