from flask import Flask

from configuration.app import Config
from .db import db


def create(blueprints=None):
    """Construct the core application."""
    app = Flask("HVALFANGST", instance_relative_config=False)
    app.config.from_object(Config)

    # Initialize Database Plugin
    db.init_app(app)

    # Register blueprints
    if blueprints:
        for blueprint in blueprints:
            app.register_blueprint(blueprint)

    # Migrate database based on registered
    with app.app_context():
        db.create_all()
        return app