"""Flask application entry point."""

import os
import secrets

from flask import Flask, render_template

from auth_routes import auth_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
    app.register_blueprint(auth_bp)

    @app.route("/login")
    def login_page():
        return render_template("login.html")

    @app.route("/register")
    def register_page():
        return render_template("register.html")

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=8000, debug=False)
