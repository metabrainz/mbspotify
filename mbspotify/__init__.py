from brainzutils.flask import CustomFlask
import os


def create_app(config_path=None):
    app = CustomFlask(
        import_name=__name__,
        use_flask_uuid=True,
    )

    # Configuration files
    app.config.from_pyfile(os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "..", "default_config.py"
    ))
    app.config.from_pyfile(os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..', 'consul_config.py'
    ), silent=True)
    app.config.from_pyfile(os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..', 'custom_config.py'
    ), silent=True)
    if config_path:
        app.config.from_pyfile(config_path)

    app.init_loggers(
        file_config=app.config.get("LOG_FILE"),
        sentry_config=app.config.get("LOG_SENTRY"),
    )

    # Blueprints
    from mbspotify.views import main_bp
    app.register_blueprint(main_bp)

    return app
