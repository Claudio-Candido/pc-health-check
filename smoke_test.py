"""End-to-end smoke test for PC Health Check MVP."""

import os
import sys

# Use a temp DB for tests
os.environ["DATABASE_URL"] = "sqlite:///smoke_test.db"

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.computer import Computer
from app.models.report import Report

app = create_app()
app.config["WTF_CSRF_ENABLED"] = False
app.config["TESTING"] = True

with app.app_context():
    db.drop_all()
    db.create_all()

client = app.test_client()

failures = []


def check(name, condition, detail=""):
    if condition:
        print(f"  OK  {name}")
    else:
        print(f"FAIL  {name} {detail}")
        failures.append(name)


print("1) Landing & auth pages")
r = client.get("/landing")
check("landing 200", r.status_code == 200)

r = client.get("/auth/register")
check("register page", r.status_code == 200)

r = client.post(
    "/auth/register",
    data={
        "email": "tech@example.com",
        "password": "secret123",
        "technician_name": "João Técnico",
        "company_name": "TechFix Lda",
    },
    follow_redirects=True,
)
check("register + login", r.status_code == 200 and b"Dashboard" in r.data)

print("2) Create computer / diagnosis")
r = client.post(
    "/computers/new",
    data={
        "client_name": "Maria Silva",
        "brand": "Dell",
        "model": "Latitude 5520",
        "processor": "Intel i7-1185G7",
        "ram": "16 GB DDR4",
        "storage": "512 GB SSD NVMe",
        "operating_system": "Windows 11 Pro",
        "analysis_date": "2026-03-20",
        "diag_performance": "bom",
        "diag_storage": "excelente",
        "diag_operating_system": "bom",
        "diag_security": "regular",
        "diag_updates": "necessita_atencao",
        "diag_overall": "bom",
        "services": ["diagnostico", "atualizacao", "limpeza"],
        "svc_desc_diagnostico": "Análise completa",
        "svc_desc_atualizacao": "Windows Update",
        "svc_desc_limpeza": "Limpeza interna",
        "recommendations": "Atualizar antivírus e instalar atualizações pendentes.",
        "notes": "Cliente reportou lentidão.",
    },
    follow_redirects=True,
)
check("create computer", r.status_code == 200 and b"Maria Silva" in r.data)

with app.app_context():
    computer = Computer.query.first()
    check("computer exists", computer is not None)
    check("diagnosis linked", computer.diagnosis is not None)
    check("services count", len(computer.services) == 3, f"got {len(computer.services)}")
    check("health score set", 0 < computer.health_score <= 100, f"score={computer.health_score}")
    print(f"     Health Score = {computer.health_score}")
    print(
        f"     Cats: P={computer.score_performance} Sys={computer.score_system} "
        f"St={computer.score_storage} Sec={computer.score_security}"
    )
    computer_id = computer.id

print("3) Generate PDF report")
r = client.post(f"/reports/generate/{computer_id}", follow_redirects=False)
check("generate redirects", r.status_code in (302, 303))
# follow to download
with app.app_context():
    report = Report.query.first()
    check("report row", report is not None)
    report_id = report.id

r = client.get(f"/reports/{report_id}/download")
check("pdf download 200", r.status_code == 200)
check("pdf content-type", r.content_type == "application/pdf")
check("pdf magic", r.data[:4] == b"%PDF")
print(f"     PDF size = {len(r.data)} bytes")

print("4) FREE plan limit (5)")
for i in range(4):
    r = client.post(f"/reports/generate/{computer_id}", follow_redirects=True)
    check(f"report {i+2}/5", r.status_code == 200)

r = client.post(f"/reports/generate/{computer_id}", follow_redirects=True)
check("6th blocked on FREE", b"Limite" in r.data or b"PRO" in r.data)

print("5) Upgrade PRO")
r = client.post(
    "/settings/billing",
    data={"action": "upgrade"},
    follow_redirects=True,
)
check("upgrade PRO", r.status_code == 200)
with app.app_context():
    user = User.query.filter_by(email="tech@example.com").first()
    check("plan is pro", user.plan == "pro")

r = client.post(f"/reports/generate/{computer_id}", follow_redirects=True)
check("report after PRO", r.status_code == 200)
with app.app_context():
    check("reports > 5", Report.query.count() > 5, f"count={Report.query.count()}")

print("6) Dashboard & lists")
for path in ["/", "/computers/", "/reports/", "/settings/", "/settings/billing"]:
    r = client.get(path)
    check(f"GET {path}", r.status_code == 200)

# cleanup
try:
    os.remove("smoke_test.db")
except OSError:
    pass

print()
if failures:
    print(f"FAILED: {len(failures)} checks — {failures}")
    sys.exit(1)
print("ALL CHECKS PASSED")
