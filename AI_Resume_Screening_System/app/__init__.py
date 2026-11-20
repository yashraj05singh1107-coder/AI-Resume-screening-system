import os
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

db = SQLAlchemy()

def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-key-change-before-deployment"),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///resume_screening.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.getenv("UPLOAD_FOLDER", "uploads"),
        MAX_CONTENT_LENGTH=int(os.getenv("MAX_CONTENT_LENGTH", 10 * 1024 * 1024)),
    )
    if test_config:
        app.config.update(test_config)

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    Path("reports").mkdir(exist_ok=True)
    db.init_app(app)

    from app import models
    from app.routes import bp
    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()

    return app
