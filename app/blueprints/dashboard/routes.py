from flask import render_template
from flask_login import current_user, login_required

from app.blueprints.dashboard import dashboard_bp
from app.models.computer import Computer
from app.models.report import Report
from app.services.plan_limits import usage_summary


@dashboard_bp.route("/")
@login_required
def index():
    computers = (
        Computer.query.filter_by(user_id=current_user.id)
        .order_by(Computer.updated_at.desc())
        .limit(8)
        .all()
    )
    recent_reports = (
        Report.query.filter_by(user_id=current_user.id)
        .order_by(Report.created_at.desc())
        .limit(5)
        .all()
    )
    total_computers = Computer.query.filter_by(user_id=current_user.id).count()
    total_reports = Report.query.filter_by(user_id=current_user.id).count()
    avg_score = 0
    if total_computers:
        scores = [
            c.health_score
            for c in Computer.query.filter_by(user_id=current_user.id).all()
            if c.health_score
        ]
        avg_score = round(sum(scores) / len(scores)) if scores else 0

    usage = usage_summary(current_user)

    return render_template(
        "dashboard/index.html",
        computers=computers,
        recent_reports=recent_reports,
        total_computers=total_computers,
        total_reports=total_reports,
        avg_score=avg_score,
        usage=usage,
    )
