import os
import secrets

from flask import Flask


def create_app() -> Flask:
    from auth_routes import auth_bp

    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
    app.register_blueprint(auth_bp)
    return app
