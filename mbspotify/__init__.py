from brainzutils.flask import CustomFlask
import os
import sys
from time import sleep

deploy_env = os.environ.get('DEPLOY_ENV', '')
CONSUL_CONFIG_FILE_RETRY_COUNT = 10

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
        '..', 'custom_config.py'
    ), silent=True)

    if deploy_env:
        config_file = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            '..', 'consul_config.py'
        )
        print("Checking if consul template generated config file exists: {}".format(config_file))
        for _ in range(CONSUL_CONFIG_FILE_RETRY_COUNT):
            if not os.path.exists(config_file):
                sleep(1)

        if not os.path.exists(config_file):
            print("No configuration file generated yet. Retried {} times, exiting.".format(CONSUL_CONFIG_FILE_RETRY_COUNT))
            sys.exit(-1)

        print("Loading consul config file {}".format(config_file))
        app.config.from_pyfile(config_file, silent=True)

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
