"""Calculate PC Health Score (0-100) from diagnosis ratings."""

RATING_POINTS = {
    "excelente": 100,
    "bom": 80,
    "regular": 55,
    "necessita_atencao": 25,
}


def _points(rating: str) -> int:
    return RATING_POINTS.get(rating, 55)


def calculate_scores(diagnosis) -> dict:
    """
    Categories:
      - Performance  <- performance
      - Sistema      <- operating_system + updates (avg)
      - Armazenamento <- storage
      - Segurança    <- security + overall (avg)
    Final score is the weighted average of the four categories.
    """
    performance = _points(diagnosis.performance)
    system = round((_points(diagnosis.operating_system) + _points(diagnosis.updates)) / 2)
    storage = _points(diagnosis.storage)
    security = round((_points(diagnosis.security) + _points(diagnosis.overall)) / 2)

    health = round((performance + system + storage + security) / 4)

    return {
        "score_performance": performance,
        "score_system": system,
        "score_storage": storage,
        "score_security": security,
        "health_score": max(0, min(100, health)),
    }


def score_label(score: int) -> str:
    if score >= 90:
        return "Excelente"
    if score >= 75:
        return "Bom"
    if score >= 55:
        return "Regular"
    return "Necessita atenção"


def score_color(score: int) -> str:
    if score >= 90:
        return "#16a34a"
    if score >= 75:
        return "#2563eb"
    if score >= 55:
        return "#d97706"
    return "#dc2626"
