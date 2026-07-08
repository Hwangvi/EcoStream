from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from app.config import configurar_cors
from app.database.database import EcoStreamRepository
from app.routers import alertas, dashboard, ia

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Ejecutando limpieza inicial de la base de datos...")
    try:
        EcoStreamRepository.purgar_datos_antiguos()
        print("Sistema listo y saneado.")
    except Exception as e:
        print(f"Error al limpiar en el inicio: {e}")
    yield
    print("Apagando EcoStream Engine...")


app = FastAPI(
    title="EcoStream Analytics Engine",
    description="Core analítico de telemetría urbana y auditoría con IA",
    lifespan=lifespan
)

configurar_cors(app)

app.include_router(alertas.router)
app.include_router(dashboard.router)
app.include_router(ia.router)
