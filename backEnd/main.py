import os
import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import EcoStreamRepository
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="EcoStream API - Monitoreo Ambiental")

r = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

CODIGOS_SENSORES = ["SEN-CENTRO-CO2", "SEN-CENTRO-RUIDO", "SEN-NORTE-TRAFICO", "SEN-SUR-CO2"]

class MedicionIn(BaseModel):
    codigo_sensor: str
    valor: float

@app.post("/api/mediciones")
async def registrar_medicion(data: MedicionIn):
    try:
        sensor_id = EcoStreamRepository.obtener_sensor_id(data.codigo_sensor)
        if not sensor_id:
            raise HTTPException(status_code=404, detail=f"El sensor {data.codigo_sensor} no existe.")
        nuevo_registro = EcoStreamRepository.insertar_medicion(sensor_id, data.valor)
        return {"status": "success", "id_medicion": nuevo_registro['id']}
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard")
async def obtener_dashboard():
    try:
        dashboard_data = []
        
        for codigo in CODIGOS_SENSORES:
            sensor_data = r.hgetall(f"sensor:{codigo}")
            
            if sensor_data:
                dashboard_data.append(sensor_data)
            else:
                dashboard_data.append({
                    "codigo_sensor": codigo,
                    "valor": "Esperando datos..."
                })
                
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer la caché de Redis: {str(e)}")