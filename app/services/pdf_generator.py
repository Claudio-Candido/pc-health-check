"""Professional PDF report generation with ReportLab."""

import os
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.models.computer import RATING_LABELS
from app.services.health_score import score_color, score_label

PAGE_W, PAGE_H = A4


def _hex_color(hex_str: str) -> colors.Color:
    hex_str = (hex_str or "#2563eb").lstrip("#")
    if len(hex_str) != 6:
        hex_str = "2563eb"
    r = int(hex_str[0:2], 16) / 255
    g = int(hex_str[2:4], 16) / 255
    b = int(hex_str[4:6], 16) / 255
    return colors.Color(r, g, b)


def _styles(brand: colors.Color):
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "TitlePT",
            parent=base["Heading1"],
            fontSize=20,
            textColor=brand,
            spaceAfter=4,
            alignment=TA_LEFT,
        ),
        "subtitle": ParagraphStyle(
            "SubtitlePT",
            parent=base["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#64748b"),
            spaceAfter=12,
        ),
        "section": ParagraphStyle(
            "SectionPT",
            parent=base["Heading2"],
            fontSize=13,
            textColor=brand,
            spaceBefore=14,
            spaceAfter=8,
        ),
        "body": ParagraphStyle(
            "BodyPT",
            parent=base["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#1e293b"),
            leading=13,
        ),
        "label": ParagraphStyle(
            "LabelPT",
            parent=base["Normal"],
            fontSize=8,
            textColor=colors.HexColor("#64748b"),
        ),
        "value": ParagraphStyle(
            "ValuePT",
            parent=base["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#0f172a"),
            leading=13,
        ),
        "score_big": ParagraphStyle(
            "ScoreBig",
            parent=base["Normal"],
            fontSize=36,
            textColor=colors.white,
            alignment=TA_CENTER,
            leading=40,
            fontName="Helvetica-Bold",
        ),
        "score_sub": ParagraphStyle(
            "ScoreSub",
            parent=base["Normal"],
            fontSize=9,
            textColor=colors.white,
            alignment=TA_CENTER,
        ),
        "footer": ParagraphStyle(
            "FooterPT",
            parent=base["Normal"],
            fontSize=8,
            textColor=colors.HexColor("#94a3b8"),
            alignment=TA_CENTER,
        ),
        "rec": ParagraphStyle(
            "RecPT",
            parent=base["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#334155"),
            leading=13,
            leftIndent=4,
        ),
    }
    return styles


def _kv_table(pairs: list[tuple[str, str]], styles, col_widths=None):
    data = []
    for label, value in pairs:
        data.append(
            [
                Paragraph(label, styles["label"]),
                Paragraph(str(value or "—"), styles["value"]),
            ]
        )
    table = Table(data, colWidths=col_widths or [55 * mm, 120 * mm])
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def generate_report_pdf(computer, user, logo_path: str | None = None) -> bytes:
    buffer = BytesIO()
    brand = _hex_color(user.brand_color)
    styles = _styles(brand)
    diagnosis = computer.diagnosis

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=f"PC Health Check — {computer.client_name}",
        author=user.company_name,
    )

    story = []

    # --- Header ---
    header_cells = []
    if logo_path and os.path.isfile(logo_path):
        try:
            img = Image(logo_path)
            img._restrictSize(40 * mm, 18 * mm)
            header_cells.append(img)
        except Exception:
            header_cells.append(Paragraph(user.company_name, styles["title"]))
    else:
        header_cells.append(Paragraph(user.company_name or "PC Health Check", styles["title"]))

    right_header = [
        Paragraph("<b>PC HEALTH CHECK</b>", styles["title"]),
        Paragraph("Relatório de Diagnóstico Técnico", styles["subtitle"]),
        Paragraph(
            f"Técnico: {user.technician_name}"
            + (f" · {user.phone}" if user.phone else ""),
            styles["label"],
        ),
    ]
    header_table = Table(
        [[header_cells[0], right_header]],
        colWidths=[70 * mm, 104 * mm],
    )
    header_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ]
        )
    )
    story.append(header_table)
    story.append(Spacer(1, 4))
    story.append(
        HRFlowable(width="100%", thickness=2, color=brand, spaceBefore=2, spaceAfter=10)
    )

    # --- Health Score banner ---
    score = computer.health_score or 0
    scolor = colors.HexColor(score_color(score))
    score_box = Table(
        [
            [
                Paragraph(str(score), styles["score_big"]),
                [
                    Paragraph("PC HEALTH SCORE", styles["score_sub"]),
                    Paragraph(score_label(score), styles["score_sub"]),
                    Spacer(1, 4),
                    Paragraph(
                        f"Performance {computer.score_performance} · "
                        f"Sistema {computer.score_system} · "
                        f"Armazenamento {computer.score_storage} · "
                        f"Segurança {computer.score_security}",
                        styles["score_sub"],
                    ),
                ],
            ]
        ],
        colWidths=[40 * mm, 134 * mm],
    )
    score_box.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), scolor),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("ROUNDEDCORNERS", [6, 6, 6, 6]),
            ]
        )
    )
    story.append(score_box)
    story.append(Spacer(1, 8))

    # --- Client & Equipment ---
    story.append(Paragraph("Dados do Cliente", styles["section"]))
    story.append(
        _kv_table(
            [
                ("Cliente", computer.client_name),
                ("Data da análise", computer.analysis_date.strftime("%d/%m/%Y")),
            ],
            styles,
        )
    )

    story.append(Paragraph("Dados do Equipamento", styles["section"]))
    story.append(
        _kv_table(
            [
                ("Marca / Modelo", f"{computer.brand} {computer.model}"),
                ("Processador", computer.processor),
                ("Memória RAM", computer.ram),
                ("Armazenamento", computer.storage),
                ("Sistema operativo", computer.operating_system),
            ],
            styles,
        )
    )

    # --- Diagnosis ---
    story.append(Paragraph("Diagnóstico", styles["section"]))
    if diagnosis:
        diag_items = [
            ("Desempenho", diagnosis.performance),
            ("Armazenamento", diagnosis.storage),
            ("Sistema operativo", diagnosis.operating_system),
            ("Segurança", diagnosis.security),
            ("Atualizações", diagnosis.updates),
            ("Estado geral", diagnosis.overall),
        ]
        diag_data = [
            [
                Paragraph("<b>Item</b>", styles["body"]),
                Paragraph("<b>Avaliação</b>", styles["body"]),
            ]
        ]
        for label, rating in diag_items:
            diag_data.append(
                [
                    Paragraph(label, styles["body"]),
                    Paragraph(RATING_LABELS.get(rating, rating), styles["body"]),
                ]
            )
        diag_table = Table(diag_data, colWidths=[90 * mm, 84 * mm])
        diag_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ]
            )
        )
        story.append(diag_table)

    # --- Category scores ---
    story.append(Paragraph("Pontuação por Categoria", styles["section"]))
    cat_data = [
        [
            Paragraph("<b>Categoria</b>", styles["body"]),
            Paragraph("<b>Pontuação</b>", styles["body"]),
        ],
        [Paragraph("Performance", styles["body"]), Paragraph(str(computer.score_performance), styles["body"])],
        [Paragraph("Sistema", styles["body"]), Paragraph(str(computer.score_system), styles["body"])],
        [Paragraph("Armazenamento", styles["body"]), Paragraph(str(computer.score_storage), styles["body"])],
        [Paragraph("Segurança", styles["body"]), Paragraph(str(computer.score_security), styles["body"])],
    ]
    cat_table = Table(cat_data, colWidths=[90 * mm, 84 * mm])
    cat_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(cat_table)

    # --- Services ---
    story.append(Paragraph("Serviços Realizados", styles["section"]))
    if computer.services:
        svc_data = [
            [
                Paragraph("<b>Serviço</b>", styles["body"]),
                Paragraph("<b>Descrição</b>", styles["body"]),
            ]
        ]
        for svc in computer.services:
            svc_data.append(
                [
                    Paragraph(svc.label, styles["body"]),
                    Paragraph(svc.description or "—", styles["body"]),
                ]
            )
        svc_table = Table(svc_data, colWidths=[70 * mm, 104 * mm])
        svc_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(svc_table)
    else:
        story.append(Paragraph("Nenhum serviço registado.", styles["body"]))

    # --- Recommendations ---
    story.append(Paragraph("Recomendações", styles["section"]))
    if computer.recommendations:
        story.append(Paragraph(computer.recommendations.replace("\n", "<br/>"), styles["rec"]))
    else:
        story.append(Paragraph("Sem recomendações adicionais.", styles["body"]))

    if computer.notes:
        story.append(Paragraph("Notas Técnicas", styles["section"]))
        story.append(Paragraph(computer.notes.replace("\n", "<br/>"), styles["rec"]))

    # --- Footer ---
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1")))
    story.append(Spacer(1, 6))
    story.append(
        Paragraph(
            f"Gerado por {user.company_name} · PC Health Check · "
            f"Relatório #{computer.id}",
            styles["footer"],
        )
    )

    doc.build(story)
    return buffer.getvalue()
