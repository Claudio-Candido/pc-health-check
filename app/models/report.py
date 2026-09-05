from datetime import datetime

from app.extensions import db


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    computer_id = db.Column(db.Integer, db.ForeignKey("computers.id"), nullable=False)
    health_score = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    owner = db.relationship("User", back_populates="reports")
    computer = db.relationship("Computer", back_populates="reports")
