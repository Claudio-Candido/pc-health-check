from flask import Blueprint

dashboard_bp = Blueprint("dashboard", __name__)

from app.blueprints.dashboard import routes  # noqa: E402, F401
