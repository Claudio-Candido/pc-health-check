from datetime import datetime

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from app.blueprints.computers import computers_bp
from app.extensions import db
from app.models.computer import (
    RATING_CHOICES,
    RATING_LABELS,
    SERVICE_CHOICES,
    SERVICE_LABELS,
    Computer,
    Diagnosis,
    ServicePerformed,
)
from app.services.health_score import calculate_scores, score_color, score_label


def _owned_computer(computer_id: int) -> Computer:
    computer = Computer.query.get_or_404(computer_id)
    if computer.user_id != current_user.id:
        abort(403)
    return computer


def _parse_date(value: str):
    if not value:
        return datetime.utcnow().date()
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return datetime.utcnow().date()


@computers_bp.route("/")
@login_required
def list_computers():
    q = (request.args.get("q") or "").strip()
    query = Computer.query.filter_by(user_id=current_user.id)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Computer.client_name.ilike(like),
                Computer.brand.ilike(like),
                Computer.model.ilike(like),
            )
        )
    computers = query.order_by(Computer.updated_at.desc()).all()
    return render_template(
        "computers/list.html",
        computers=computers,
        q=q,
        score_label=score_label,
        score_color=score_color,
    )


@computers_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        computer = Computer(
            user_id=current_user.id,
            client_name=(request.form.get("client_name") or "").strip(),
            brand=(request.form.get("brand") or "").strip(),
            model=(request.form.get("model") or "").strip(),
            processor=(request.form.get("processor") or "").strip(),
            ram=(request.form.get("ram") or "").strip(),
            storage=(request.form.get("storage") or "").strip(),
            operating_system=(request.form.get("operating_system") or "").strip(),
            analysis_date=_parse_date(request.form.get("analysis_date")),
            notes=(request.form.get("notes") or "").strip() or None,
            recommendations=(request.form.get("recommendations") or "").strip() or None,
        )

        required = [
            computer.client_name,
            computer.brand,
            computer.model,
            computer.processor,
            computer.ram,
            computer.storage,
            computer.operating_system,
        ]
        if not all(required):
            flash("Preencha todos os campos obrigatórios do equipamento.", "danger")
            return render_template(
                "computers/form.html",
                computer=computer,
                diagnosis=None,
                selected_services=[],
                service_descriptions={},
                rating_choices=RATING_CHOICES,
                rating_labels=RATING_LABELS,
                service_choices=SERVICE_CHOICES,
                service_labels=SERVICE_LABELS,
                mode="create",
            )

        def _rating(name: str) -> str:
            val = request.form.get(name) or "bom"
            return val if val in RATING_CHOICES else "bom"

        diagnosis = Diagnosis(
            performance=_rating("diag_performance"),
            storage=_rating("diag_storage"),
            operating_system=_rating("diag_operating_system"),
            security=_rating("diag_security"),
            updates=_rating("diag_updates"),
            overall=_rating("diag_overall"),
        )
        computer.diagnosis = diagnosis

        scores = calculate_scores(diagnosis)
        for key, value in scores.items():
            setattr(computer, key, value)

        selected = request.form.getlist("services")
        for svc in selected:
            if svc in SERVICE_CHOICES:
                desc = (request.form.get(f"svc_desc_{svc}") or "").strip() or None
                computer.services.append(
                    ServicePerformed(service_type=svc, description=desc)
                )

        db.session.add(computer)
        db.session.commit()
        flash("Computador registado com sucesso.", "success")
        return redirect(url_for("computers.detail", computer_id=computer.id))

    return render_template(
        "computers/form.html",
        computer=None,
        diagnosis=None,
        selected_services=[],
        service_descriptions={},
        rating_choices=RATING_CHOICES,
        rating_labels=RATING_LABELS,
        service_choices=SERVICE_CHOICES,
        service_labels=SERVICE_LABELS,
        mode="create",
    )


@computers_bp.route("/<int:computer_id>")
@login_required
def detail(computer_id):
    computer = _owned_computer(computer_id)
    return render_template(
        "computers/detail.html",
        computer=computer,
        rating_labels=RATING_LABELS,
        score_label=score_label,
        score_color=score_color,
    )


@computers_bp.route("/<int:computer_id>/edit", methods=["GET", "POST"])
@login_required
def edit(computer_id):
    computer = _owned_computer(computer_id)
    diagnosis = computer.diagnosis

    if request.method == "POST":
        computer.client_name = (request.form.get("client_name") or "").strip()
        computer.brand = (request.form.get("brand") or "").strip()
        computer.model = (request.form.get("model") or "").strip()
        computer.processor = (request.form.get("processor") or "").strip()
        computer.ram = (request.form.get("ram") or "").strip()
        computer.storage = (request.form.get("storage") or "").strip()
        computer.operating_system = (request.form.get("operating_system") or "").strip()
        computer.analysis_date = _parse_date(request.form.get("analysis_date"))
        computer.notes = (request.form.get("notes") or "").strip() or None
        computer.recommendations = (
            request.form.get("recommendations") or ""
        ).strip() or None

        if not all(
            [
                computer.client_name,
                computer.brand,
                computer.model,
                computer.processor,
                computer.ram,
                computer.storage,
                computer.operating_system,
            ]
        ):
            flash("Preencha todos os campos obrigatórios do equipamento.", "danger")
        else:
            def _rating(name: str) -> str:
                val = request.form.get(name) or "bom"
                return val if val in RATING_CHOICES else "bom"

            if diagnosis is None:
                diagnosis = Diagnosis(computer=computer)
                db.session.add(diagnosis)

            diagnosis.performance = _rating("diag_performance")
            diagnosis.storage = _rating("diag_storage")
            diagnosis.operating_system = _rating("diag_operating_system")
            diagnosis.security = _rating("diag_security")
            diagnosis.updates = _rating("diag_updates")
            diagnosis.overall = _rating("diag_overall")

            scores = calculate_scores(diagnosis)
            for key, value in scores.items():
                setattr(computer, key, value)

            computer.services.clear()
            selected = request.form.getlist("services")
            for svc in selected:
                if svc in SERVICE_CHOICES:
                    desc = (request.form.get(f"svc_desc_{svc}") or "").strip() or None
                    computer.services.append(
                        ServicePerformed(service_type=svc, description=desc)
                    )

            db.session.commit()
            flash("Registo atualizado.", "success")
            return redirect(url_for("computers.detail", computer_id=computer.id))

    selected_services = [s.service_type for s in computer.services]
    service_descriptions = {s.service_type: s.description or "" for s in computer.services}

    return render_template(
        "computers/form.html",
        computer=computer,
        diagnosis=diagnosis,
        selected_services=selected_services,
        service_descriptions=service_descriptions,
        rating_choices=RATING_CHOICES,
        rating_labels=RATING_LABELS,
        service_choices=SERVICE_CHOICES,
        service_labels=SERVICE_LABELS,
        mode="edit",
    )


@computers_bp.route("/<int:computer_id>/delete", methods=["POST"])
@login_required
def delete(computer_id):
    computer = _owned_computer(computer_id)
    db.session.delete(computer)
    db.session.commit()
    flash("Computador eliminado.", "info")
    return redirect(url_for("computers.list_computers"))
