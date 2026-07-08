from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.database.database import EcoStreamRepository
from app.services.pdf_service import generar_reporte_pdf
from app.utils.kafka_helper import crear_productor

router = APIRouter(prefix="/api/alertas", tags=["Alertas"])


@router.get("/exportar")
async def exportar_registro_pdf():
    try:
        filas = EcoStreamRepository.obtener_ultimas_100_filas()

        if not filas:
            return {"status": "error", "message": "No se encontraron registros en este rango de tiempo."}

        if len(filas) > 500:
            filas = filas[:500]

        buffer = generar_reporte_pdf(filas)

        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=Reporte_EcoStream.pdf"}
        )
    except Exception as e:
        print(f"ERROR CRÍTICO: {e}")
        raise HTTPException(status_code=500, detail="Error en servidor")


@router.get("/conteo")
async def contar_alertas(rango: int = 1):
    count = EcoStreamRepository.contar_alertas(rango)
    return {"total": count}


@router.post("/inyectar-anomalia")
async def inyectar_anomalia(zona: str):
    payload = {
        "codigo_sensor": f"SEN-{zona.upper()}-CO2",
        "valor": 999.0
    }

    producer = crear_productor()
    producer.send('telemetria-sensores', value=payload)
    producer.flush()
    producer.close()

    return {"status": "Anomalía inyectada correctamente"}


@router.post("/reset")
async def reset_alertas():
    try:
        EcoStreamRepository.limpiar_alertas()
        return {"status": "success", "message": "Historial de alertas limpiado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al limpiar: {str(e)}")


@router.get("")
async def obtener_alertas():
    try:
        return EcoStreamRepository.obtener_alertas_recientes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
