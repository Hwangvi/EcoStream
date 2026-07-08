import os
import json
from openai import OpenAI


def analizar_alertas_con_llm(alertas_zona, zona):
    if not alertas_zona:
        reporte_texto = f"Métricas estables en el cuadrante {zona}. No se registran picos críticos de contaminación."
    else:
        reporte_texto = f"--- INICIO REPORTE ANOMALÍAS - ÁREA: {zona} ---\n"
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
    return resultado_ia
