import os

from dotenv import load_dotenv
from flask import Flask, redirect, url_for

from app.config import Config
from app.extensions import csrf, db, login_manager

load_dotenv()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.blueprints.auth import auth_bp
    from app.blueprints.computers import computers_bp
    from app.blueprints.dashboard import dashboard_bp
    from app.blueprints.reports import reports_bp
    from app.blueprints.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(computers_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)

    @app.route("/landing")
    def landing():
        from flask import render_template
        from flask_login import current_user

        if current_user.is_authenticated:
            return redirect(url_for("dashboard.index"))
        return render_template("landing.html")

    # Override dashboard root for guests → landing page
    @app.before_request
    def _guest_home_to_landing():
        from flask import request
        from flask_login import current_user

        if (
            request.endpoint == "dashboard.index"
            and not current_user.is_authenticated
        ):
            return redirect(url_for("landing"))

    with app.app_context():
        db.create_all()

    return app
