from datetime import date, datetime

from app.extensions import db

RATING_CHOICES = ("excelente", "bom", "regular", "necessita_atencao")
SERVICE_CHOICES = (
    "diagnostico",
    "atualizacao",
    "configuracao",
    "backup",
    "instalacao_software",
    "limpeza",
    "outros",
)

RATING_LABELS = {
    "excelente": "Excelente",
    "bom": "Bom",
    "regular": "Regular",
    "necessita_atencao": "Necessita atenção",
}

SERVICE_LABELS = {
    "diagnostico": "Diagnóstico",
    "atualizacao": "Atualização",
    "configuracao": "Configuração",
    "backup": "Backup",
    "instalacao_software": "Instalação de software legítimo",
    "limpeza": "Limpeza",
    "outros": "Outros",
}


class Computer(db.Model):
    __tablename__ = "computers"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    client_name = db.Column(db.String(150), nullable=False)
    brand = db.Column(db.String(80), nullable=False)
    model = db.Column(db.String(120), nullable=False)
    processor = db.Column(db.String(150), nullable=False)
    ram = db.Column(db.String(80), nullable=False)
    storage = db.Column(db.String(120), nullable=False)
    operating_system = db.Column(db.String(120), nullable=False)
    analysis_date = db.Column(db.Date, nullable=False, default=date.today)

    notes = db.Column(db.Text)
    recommendations = db.Column(db.Text)

    score_performance = db.Column(db.Integer, default=0)
    score_system = db.Column(db.Integer, default=0)
    score_storage = db.Column(db.Integer, default=0)
    score_security = db.Column(db.Integer, default=0)
    health_score = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = db.relationship("User", back_populates="computers")
    diagnosis = db.relationship(
        "Diagnosis",
        back_populates="computer",
        uselist=False,
        cascade="all, delete-orphan",
    )
    services = db.relationship(
        "ServicePerformed",
        back_populates="computer",
        cascade="all, delete-orphan",
        order_by="ServicePerformed.id",
    )
    reports = db.relationship("Report", back_populates="computer", cascade="all, delete-orphan")

    def display_name(self) -> str:
        return f"{self.brand} {self.model}"


class Diagnosis(db.Model):
    __tablename__ = "diagnoses"

    id = db.Column(db.Integer, primary_key=True)
    computer_id = db.Column(
        db.Integer, db.ForeignKey("computers.id"), nullable=False, unique=True
    )

    performance = db.Column(db.String(30), nullable=False, default="bom")
    storage = db.Column(db.String(30), nullable=False, default="bom")
    operating_system = db.Column(db.String(30), nullable=False, default="bom")
    security = db.Column(db.String(30), nullable=False, default="bom")
    updates = db.Column(db.String(30), nullable=False, default="bom")
    overall = db.Column(db.String(30), nullable=False, default="bom")

    computer = db.relationship("Computer", back_populates="diagnosis")

    def as_dict(self) -> dict:
        return {
            "performance": self.performance,
            "storage": self.storage,
            "operating_system": self.operating_system,
            "security": self.security,
            "updates": self.updates,
            "overall": self.overall,
        }


class ServicePerformed(db.Model):
    __tablename__ = "services_performed"

    id = db.Column(db.Integer, primary_key=True)
    computer_id = db.Column(db.Integer, db.ForeignKey("computers.id"), nullable=False)
    service_type = db.Column(db.String(40), nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    computer = db.relationship("Computer", back_populates="services")

    @property
    def label(self) -> str:
        return SERVICE_LABELS.get(self.service_type, self.service_type)
