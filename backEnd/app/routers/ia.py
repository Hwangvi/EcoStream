from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database.database import EcoStreamRepository
from app.services.ia_service import analizar_alertas_con_llm

router = APIRouter(prefix="/api/ia", tags=["IA"])


class PeticionAnalisis(BaseModel):
    zona: str


@router.post("/analizar")
async def analizar_zona_con_ia(data: PeticionAnalisis):
    try:
        filas = EcoStreamRepository.obtener_alertas_recientes()

        alertas_zona = []
        for f in filas:
            alerta_dict = dict(f)
            codigo = str(alerta_dict.get("codigo_sensor", ""))

            if data.zona == "TODAS" or f"-{data.zona}-" in codigo:
                try:
                    valor_num = float(alerta_dict.get("valor_disparado", 0.0))
                except (ValueError, TypeError):
                    valor_num = 0.0

                alertas_zona.append({
                    "codigo": codigo,
                    "valor": valor_num,
                    "descripcion": str(alerta_dict.get("descripcion", "Anomalía territorial."))
                })

        resultado_ia = analizar_alertas_con_llm(alertas_zona, data.zona)

        return {
            "status": "success",
            "zona_auditada": data.zona,
            "alertas_procesadas": len(alertas_zona),
            "diagnostico": resultado_ia.get("diagnostico", "Auditoría no concluyente."),
            "recomendaciones": resultado_ia.get("recomendaciones", [])
        }

    except Exception as e:
        print(f"Fallo en Agente Cognitivo Groq: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analítico del LLM: {str(e)}.")
