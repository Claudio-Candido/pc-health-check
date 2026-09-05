from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.blueprints.auth import auth_bp
from app.extensions import db
from app.models.user import User


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        technician_name = (request.form.get("technician_name") or "").strip()
        company_name = (request.form.get("company_name") or "").strip() or "Minha Empresa"

        errors = []
        if not email or "@" not in email:
            errors.append("Email inválido.")
        if len(password) < 6:
            errors.append("A palavra-passe deve ter pelo menos 6 caracteres.")
        if not technician_name:
            errors.append("Nome do técnico é obrigatório.")
        if User.query.filter_by(email=email).first():
            errors.append("Este email já está registado.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template(
                "auth/register.html",
                email=email,
                technician_name=technician_name,
                company_name=company_name,
            )

        user = User(
            email=email,
            technician_name=technician_name,
            company_name=company_name,
            plan="free",
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Conta criada com sucesso! Bem-vindo ao PC Health Check.", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=bool(request.form.get("remember")))
            next_url = request.args.get("next")
            flash(f"Olá, {user.technician_name}!", "success")
            return redirect(next_url or url_for("dashboard.index"))
        flash("Email ou palavra-passe incorretos.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sessão terminada.", "info")
    return redirect(url_for("auth.login"))
