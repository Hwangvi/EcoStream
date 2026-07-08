from fastapi import APIRouter, HTTPException
from app.database.database import EcoStreamRepository

router = APIRouter(prefix="/api", tags=["Dashboard"])


@router.get("/dashboard")
async def obtener_dashboard():
    try:
        return EcoStreamRepository.obtener_ultimas_mediciones()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
