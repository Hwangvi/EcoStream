import os
import io
import json
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai import OpenAI
from dotenv import load_dotenv
from app.database.database import EcoStreamRepository, get_db_connection

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

load_dotenv()

app = FastAPI(
    title="EcoStream Analytics Engine",
    description="Core analítico de telemetría urbana y auditoría con IA"
)

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PeticionAnalisis(BaseModel):
    zona: str

@app.get("/api/alertas/exportar")
async def exportar_registro_pdf(rango: str = "dia"):
    ahora = datetime.now()
    fecha_limite = ahora - timedelta(days=1)
    if rango == "semana": fecha_limite = ahora - timedelta(days=7)
    elif rango == "mes": fecha_limite = ahora - timedelta(days=30)

    filas = EcoStreamRepository.exportar_alertas_por_fecha(fecha_limite)
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=20, leftMargin=15, title="Reporte de Auditoría EcoStream",
    author="EcoStream Analytics Engine")
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph(f"Reporte de Auditoría: {rango.upper()}", styles['Title']))
    elements.append(Spacer(1, 12))

    data = [["ID", "Sensor", "Valor", "Descrip.", "Fecha"]]
    for f in filas:
        desc_paragraph = Paragraph(f['descripcion'], styles['Normal'])
        data.append([str(f['id']), 
            f['codigo_sensor'], 
            str(f['valor_disparado']), 
            desc_paragraph,
            str(f['fecha_alerta'])[:16]])


    table = Table(data, colWidths=[30, 100, 45, 250, 80])
    table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", 
                             headers={"Content-Disposition": f"attachment; filename=Reporte.pdf"})
@app.post("/api/ia/analizar")
async def analizar_zona_con_ia(data: PeticionAnalisis):
    try:
        filas = EcoStreamRepository.obtener_alertas_recientes()
        
        alertas_zona = []
        for f in filas:
            alerta_dict = dict(f)
            codigo = str(alerta_dict.get("codigo_sensor", ""))
            
            if data.zona == "TODAS" or f"-{data.zona}-" in codigo:
                try: valor_num = float(alerta_dict.get("valor_disparado", 0.0))
                except: valor_num = 0.0

                alertas_zona.append({
                    "codigo": codigo,
                    "valor": valor_num,
                    "descripcion": str(alerta_dict.get("descripcion", "Anomalía territorial."))
                })

        if not alertas_zona:
            reporte_texto = f"Métricas estables en el cuadrante {data.zona}. No se registran picos críticos de contaminación."
        else:
            reporte_texto = f"--- INICIO REPORTE ANOMALÍAS - ÁREA: {data.zona} ---\n"
            for idx, a in enumerate(alertas_zona):
                reporte_texto += f"Incidente #{idx+1}: Dispositivo {a['codigo']} | Valor: {a['valor']} | Diagnóstico: {a['descripcion']}\n"
            reporte_texto += "--- FIN REPORTE ---"

        client_groq = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY")
        )

        system_prompt = (
            "Eres un experto senior en Smart Cities y resiliencia medioambiental urbana. Tu tarea es auditar un log "
            "de métricas críticas y dictaminar un plan de mitigación técnica inmediato.\n\n"
            "Debes responder OBLIGATORIAMENTE con un objeto JSON estructurado que contenga exactamente estas dos llaves:\n"
            "1. 'diagnostico': Evaluación profesional del estado del cuadrante urbano (máximo 3 líneas).\n"
            "2. 'recomendaciones': Un array de strings (máximo 3) con soluciones de infraestructura concretas.\n\n"
            "Ejemplo estricto de salida:\n"
            '{"diagnostico": "Análisis...", "recomendaciones": ["Medida 1", "Medida 2"]}'
        )

        response = client_groq.chat.completions.create(
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"},  
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Audita el siguiente reporte de telemetría urbana:\n\n{reporte_texto}"}
            ],
            temperature=0.2
        )

        resultado_ia = json.loads(response.choices[0].message.content)

        return {
            "status": "success",
            "zona_auditada": data.zona,
            "alertas_procesadas": len(alertas_zona),
            "diagnostico": resultado_ia.get("diagnostico", "Auditoría no concluyente."),
            "recomendaciones": resultado_ia.get("recomendaciones", [])
        }
        
    except Exception as e:
        print(f"⚠️ Fallo en Agente Cognitivo Groq: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analítico del LLM: {str(e)}.")


@app.get("/api/dashboard")
async def obtener_dashboard():
    try:
        return EcoStreamRepository.obtener_ultimas_mediciones()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/alertas")
async def obtener_alertas():
    try:
        return EcoStreamRepository.obtener_alertas_recientes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))