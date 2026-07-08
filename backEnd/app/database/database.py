import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from sqlmodel import create_engine, Session, select, func, text, delete
from dotenv import load_dotenv

from app.domain.models import Barrio, Sensor, Medicion, Alerta

load_dotenv()

REQUIRED_ENV_VARS = ["DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD"]
for var in REQUIRED_ENV_VARS:
    if not os.getenv(var):
        print(f"ERROR CRITICO: La variable de entorno {var} no esta definida.")
        sys.exit(1)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=10, echo=False)
print("Engine de SQLModel conectado a PostgreSQL.")


def get_session():
    return Session(engine)


class EcoStreamRepository:

    @staticmethod
    def obtener_sensor_id(codigo_sensor: str):
        with get_session() as session:
            sensor = session.exec(
                select(Sensor).where(Sensor.codigo_sensor == codigo_sensor)
            ).first()
            return sensor.id if sensor else None

    @staticmethod
    def insertar_medicion(sensor_id: int, valor: float):
        with get_session() as session:
            medicion = Medicion(sensor_id=sensor_id, valor=Decimal(str(valor)))
            session.add(medicion)
            session.commit()
            session.refresh(medicion)
            return {"id": medicion.id, "fecha_registro": medicion.fecha_registro}

    @staticmethod
    def obtener_ultimas_mediciones():
        with get_session() as session:
            subq = (
                select(func.max(Medicion.fecha_registro))
                .group_by(Medicion.sensor_id)
                .scalar_subquery()
            )
            results = session.exec(
                select(
                    Sensor.codigo_sensor,
                    Barrio.nombre.label("barrio"),
                    Sensor.tipo,
                    Sensor.unidad_medida,
                    Medicion.valor,
                    Medicion.fecha_registro,
                )
                .join(Sensor, Medicion.sensor_id == Sensor.id)
                .join(Barrio, Sensor.barrio_id == Barrio.id)
                .where(Medicion.fecha_registro.in_(select(subq)))
            ).all()

            return [
                {
                    "codigo_sensor": r.codigo_sensor,
                    "barrio": r.barrio,
                    "tipo": r.tipo,
                    "unidad_medida": r.unidad_medida,
                    "valor": float(r.valor),
                    "fecha_registro": str(r.fecha_registro),
                }
                for r in results
            ]

    @staticmethod
    def insertar_alerta(sensor_id: int, valor: float, descripcion: str):
        with get_session() as session:
            alerta = Alerta(
                sensor_id=sensor_id,
                valor_disparado=Decimal(str(valor)),
                descripcion=descripcion,
            )
            session.add(alerta)
            session.commit()
            session.refresh(alerta)
            return {
                "id": alerta.id,
                "fecha_alerta": alerta.fecha_alerta,
                "valor_disparado": float(alerta.valor_disparado),
            }

    @staticmethod
    def obtener_alertas_recientes():
        with get_session() as session:
            results = session.exec(
                select(
                    Alerta.id,
                    Sensor.codigo_sensor,
                    Alerta.valor_disparado,
                    Alerta.descripcion,
                    Alerta.fecha_alerta,
                )
                .join(Sensor, Alerta.sensor_id == Sensor.id)
                .order_by(Alerta.fecha_alerta.desc())
                .limit(10)
            ).all()

            return [
                {
                    "id": r.id,
                    "codigo_sensor": r.codigo_sensor,
                    "valor_disparado": float(r.valor_disparado),
                    "descripcion": r.descripcion,
                    "fecha_alerta": str(r.fecha_alerta),
                }
                for r in results
            ]

    @staticmethod
    def obtener_datos_auditoria_unificados(fecha_inicio):
        query = text("""
            SELECT * FROM (
                SELECT 'MEDICION' as tipo, m.fecha_registro as fecha_evento, s.codigo_sensor, m.valor::DECIMAL(10,2) as valor, 'Promedio operacional' as descripcion
                FROM mediciones m JOIN sensores s ON m.sensor_id = s.id
                UNION ALL
                SELECT 'ALERTA' as tipo, a.fecha_alerta as fecha_evento, s.codigo_sensor, a.valor_disparado::DECIMAL(10,2) as valor, a.descripcion
                FROM alertas a JOIN sensores s ON a.sensor_id = s.id
            ) as union_tabla
            WHERE fecha_evento >= :fecha_inicio
            ORDER BY fecha_evento DESC
        """)
        with get_session() as session:
            results = session.exec(query, {"fecha_inicio": fecha_inicio.isoformat()}).all()
            return [dict(r._mapping) for r in results]

    @staticmethod
    def exportar_alertas_por_fecha(fecha_inicio):
        with get_session() as session:
            results = session.exec(
                select(
                    Alerta.id,
                    Sensor.codigo_sensor,
                    Alerta.valor_disparado,
                    Alerta.descripcion,
                    Alerta.fecha_alerta,
                )
                .join(Sensor, Alerta.sensor_id == Sensor.id)
                .where(Alerta.fecha_alerta >= fecha_inicio)
                .order_by(Alerta.fecha_alerta.desc())
            ).all()

            return [
                {
                    "id": r.id,
                    "codigo_sensor": r.codigo_sensor,
                    "valor_disparado": float(r.valor_disparado),
                    "descripcion": r.descripcion,
                    "fecha_alerta": str(r.fecha_alerta),
                }
                for r in results
            ]

    @staticmethod
    def limpiar_alertas():
        with get_session() as session:
            session.exec(text("TRUNCATE TABLE alertas RESTART IDENTITY"))
            session.commit()

    @staticmethod
    def purgar_datos_antiguos():
        with get_session() as session:
            limite = datetime.now() - timedelta(days=7)
            session.exec(
                delete(Medicion).where(Medicion.fecha_registro < limite)
            )
            session.commit()

    @staticmethod
    def contar_alertas(dias):
        with get_session() as session:
            limite = datetime.now() - timedelta(days=dias)
            count = session.exec(
                select(func.count()).select_from(Alerta).where(Alerta.fecha_alerta >= limite)
            ).one()
            return count or 0

    @staticmethod
    def obtener_ultimas_100_filas():
        query = text("""
            SELECT * FROM (
                SELECT 'MEDICION' as tipo, m.fecha_registro as fecha_evento, s.codigo_sensor, m.valor::DECIMAL(10,2) as valor, 'Promedio operacional' as descripcion
                FROM mediciones m JOIN sensores s ON m.sensor_id = s.id
                UNION ALL
                SELECT 'ALERTA' as tipo, a.fecha_alerta as fecha_evento, s.codigo_sensor, a.valor_disparado::DECIMAL(10,2) as valor, a.descripcion
                FROM alertas a JOIN sensores s ON a.sensor_id = s.id
            ) as union_tabla
            ORDER BY fecha_evento DESC LIMIT 100
        """)
        with get_session() as session:
            results = session.exec(query).all()
            return [dict(r._mapping) for r in results]
