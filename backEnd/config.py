import os
from fastapi.middleware.cors import CORSMiddleware


def configurar_cors(app):
    origins_raw = os.getenv("CORS_ORIGINS", "http://localhost:5173")

    origenes_permitidos = [url.strip() for url in origins_raw.split(",")]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origenes_permitidos,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )