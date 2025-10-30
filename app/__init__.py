from flask import Flask, Blueprint, session
from app.main import main
import logging, uuid, os
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config["DEBUG"] = True
    app.config["START_TIME"] = datetime.now()
    app.secret_key = "CaptureTheFlag"

    app.register_blueprint(main)

    return app
