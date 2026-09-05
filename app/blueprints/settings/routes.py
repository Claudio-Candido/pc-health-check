import os
import uuid

from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app.blueprints.settings import settings_bp
from app.extensions import db
from app.services.plan_limits import usage_summary


def _allowed_file(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


@settings_bp.route("/", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        current_user.technician_name = (
            request.form.get("technician_name") or ""
        ).strip() or current_user.technician_name
        current_user.company_name = (
            request.form.get("company_name") or ""
        ).strip() or current_user.company_name
        current_user.phone = (request.form.get("phone") or "").strip() or None

        brand_color = (request.form.get("brand_color") or "").strip()
        if brand_color.startswith("#") and len(brand_color) == 7:
            if current_user.is_pro:
                current_user.brand_color = brand_color
            else:
                flash("Personalização de cor disponível apenas no plano PRO.", "warning")

        logo = request.files.get("logo")
        if logo and logo.filename:
            if not current_user.is_pro:
                flash("Upload de logotipo disponível apenas no plano PRO.", "warning")
            elif not _allowed_file(logo.filename):
                flash("Formato de imagem não suportado.", "danger")
            else:
                os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
                ext = secure_filename(logo.filename).rsplit(".", 1)[1].lower()
                filename = f"user{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
                path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                logo.save(path)
                if current_user.logo_filename:
                    old = os.path.join(
                        current_app.config["UPLOAD_FOLDER"], current_user.logo_filename
                    )
                    if os.path.isfile(old):
                        try:
                            os.remove(old)
                        except OSError:
                            pass
                current_user.logo_filename = filename
                flash("Logotipo atualizado.", "success")

        db.session.commit()
        flash("Definições guardadas.", "success")
        return redirect(url_for("settings.profile"))

    return render_template(
        "settings/profile.html",
        usage=usage_summary(current_user),
    )


@settings_bp.route("/billing", methods=["GET", "POST"])
@login_required
def billing():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "upgrade":
            current_user.plan = "pro"
            db.session.commit()
            flash("Upgrade para PRO ativado! Relatórios ilimitados e personalização liberados.", "success")
        elif action == "downgrade":
            current_user.plan = "free"
            db.session.commit()
            flash("Plano alterado para FREE.", "info")
        return redirect(url_for("settings.billing"))

    return render_template(
        "settings/billing.html",
        usage=usage_summary(current_user),
    )
