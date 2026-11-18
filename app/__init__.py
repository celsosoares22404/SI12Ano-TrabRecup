import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
    else:
        os.makedirs(app.instance_path, exist_ok=True)
        database_url = f"sqlite:///{os.path.join(app.instance_path, 'tarefas.db')}"

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "chave-local-para-desenvolvimento"),
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping": True},
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    from app import routes

    app.register_blueprint(routes.bp)

    with app.app_context():
        from app import models

        db.create_all()

    return app
