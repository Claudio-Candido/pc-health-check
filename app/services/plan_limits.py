from datetime import datetime

from flask import current_app

from app.extensions import db
from app.models.report import Report


def reports_used_this_month(user) -> int:
    now = datetime.utcnow()
    start = datetime(now.year, now.month, 1)
    return (
        Report.query.filter(
            Report.user_id == user.id,
            Report.created_at >= start,
        ).count()
    )


def report_limit(user) -> int | None:
    """None means unlimited (PRO)."""
    if user.is_pro:
        return None
    return current_app.config.get("FREE_REPORTS_PER_MONTH", 5)


def can_generate_report(user) -> tuple[bool, str]:
    limit = report_limit(user)
    if limit is None:
        return True, ""
    used = reports_used_this_month(user)
    if used >= limit:
        return (
            False,
            f"Limite do plano FREE atingido ({limit} relatórios/mês). "
            "Faça upgrade para PRO para relatórios ilimitados.",
        )
    return True, ""


def usage_summary(user) -> dict:
    limit = report_limit(user)
    used = reports_used_this_month(user)
    return {
        "plan": user.plan,
        "used": used,
        "limit": limit,
        "remaining": None if limit is None else max(0, limit - used),
        "unlimited": limit is None,
    }
