import io
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def generar_reporte_pdf(filas):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        title="Reporte de Auditoría - EcoStream",
        author="HwangVi",
        subject="Reporte técnico de alertas y mediciones"
    )
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Reporte de Auditoría: Últimos 100 registros", styles['Title']))
    elements.append(Spacer(1, 12))

    data = [["Tipo", "Sensor", "Valor", "Descripción", "Fecha/Hora"]]

    for f in filas:
        tipo = f.get('tipo') or 'Desconocido'
        codigo = f.get('codigo_sensor') or 'S/C'
        valor = f.get('valor') or 0.0
        desc = f.get('descripcion') or 'Sin descripción'
        fecha = str(f.get('fecha_evento'))[:16] if f.get('fecha_evento') else "N/A"

        es_alerta = tipo == 'ALERTA'
        color_texto = colors.red if es_alerta else colors.black

        fila = [
            tipo,
            Paragraph(f"<font color='{color_texto}'>{codigo}</font>", styles['Normal']),
            Paragraph(f"<font color='{color_texto}'>{str(round(float(valor), 2))}</font>", styles['Normal']),
            Paragraph(f"<font color='{color_texto}'>{desc}</font>", styles['Normal']),
            fecha
        ]
        data.append(fila)

    table = Table(data, colWidths=[60, 100, 60, 250, 100])
    table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return buffer
