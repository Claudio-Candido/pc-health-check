import os

from flask import (
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    send_file,
    url_for,
)
from flask_login import current_user, login_required
from io import BytesIO

from app.blueprints.reports import reports_bp
from app.extensions import db
from app.models.computer import Computer, RATING_LABELS
from app.models.report import Report
from app.services.health_score import score_color, score_label
from app.services.pdf_generator import generate_report_pdf
from app.services.plan_limits import can_generate_report, usage_summary


def _owned_computer(computer_id: int) -> Computer:
    computer = Computer.query.get_or_404(computer_id)
    if computer.user_id != current_user.id:
        abort(403)
    return computer


@reports_bp.route("/")
@login_required
def list_reports():
    reports = (
        Report.query.filter_by(user_id=current_user.id)
        .order_by(Report.created_at.desc())
        .all()
    )
    usage = usage_summary(current_user)
    return render_template(
        "reports/list.html",
        reports=reports,
        usage=usage,
        score_label=score_label,
        score_color=score_color,
    )


@reports_bp.route("/generate/<int:computer_id>", methods=["POST"])
@login_required
def generate(computer_id):
    computer = _owned_computer(computer_id)
    if not computer.diagnosis:
        flash("Complete o diagnóstico antes de gerar o relatório.", "warning")
        return redirect(url_for("computers.detail", computer_id=computer.id))

    ok, message = can_generate_report(current_user)
    if not ok:
        flash(message, "danger")
        return redirect(url_for("settings.billing"))

    report = Report(
        user_id=current_user.id,
        computer_id=computer.id,
        health_score=computer.health_score or 0,
    )
    db.session.add(report)
    db.session.commit()
    flash("Relatório gerado. Pode descarregar o PDF.", "success")
    return redirect(url_for("reports.download", report_id=report.id))


@reports_bp.route("/<int:report_id>/download")
@login_required
def download(report_id):
    report = Report.query.get_or_404(report_id)
    if report.user_id != current_user.id:
        abort(403)

    computer = report.computer
    logo_path = None
    if current_user.logo_filename:
        candidate = os.path.join(
            current_app.config["UPLOAD_FOLDER"], current_user.logo_filename
        )
        if os.path.isfile(candidate):
            logo_path = candidate

    pdf_bytes = generate_report_pdf(computer, current_user, logo_path=logo_path)
    filename = (
        f"pc-health-{computer.client_name.replace(' ', '-')}-{report.id}.pdf"
    )
    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )


@reports_bp.route("/preview/<int:computer_id>")
@login_required
def preview(computer_id):
    computer = _owned_computer(computer_id)
    return render_template(
        "reports/preview.html",
        computer=computer,
        rating_labels=RATING_LABELS,
        score_label=score_label,
        score_color=score_color,
        usage=usage_summary(current_user),
    )
