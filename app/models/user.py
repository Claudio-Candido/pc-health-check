from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    company_name = db.Column(db.String(150), nullable=False, default="Minha Empresa")
    technician_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(40))
    plan = db.Column(db.String(20), nullable=False, default="free")  # free | pro
    logo_filename = db.Column(db.String(255))
    brand_color = db.Column(db.String(7), default="#2563eb")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    computers = db.relationship("Computer", back_populates="owner", lazy="dynamic")
    reports = db.relationship("Report", back_populates="owner", lazy="dynamic")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_pro(self) -> bool:
        return self.plan == "pro"

    def logo_url(self) -> str | None:
        if self.logo_filename:
            return f"/static/uploads/logos/{self.logo_filename}"
        return None
