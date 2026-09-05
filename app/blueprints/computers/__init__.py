from flask import Blueprint

computers_bp = Blueprint("computers", __name__, url_prefix="/computers")

from app.blueprints.computers import routes  # noqa: E402, F401
