import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "ecostream"),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD")
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)


class EcoStreamRepository:
    
    @staticmethod
    def obtener_sensor_id(codigo_sensor: str):
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM sensores WHERE codigo_sensor = %s", (codigo_sensor,))
                sensor = cursor.fetchone()
                return sensor['id'] if sensor else None

    @staticmethod
    def insertar_medicion(sensor_id: int, valor: float):
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO mediciones (sensor_id, valor) VALUES (%s, %s) RETURNING id, fecha_registro",
                    (sensor_id, valor)
                )
                nuevo_registro = cursor.fetchone()
                conn.commit()
                return nuevo_registro

    @staticmethod
    def obtener_ultimas_mediciones():
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        s.codigo_sensor, 
                        b.nombre as barrio, 
                        s.tipo, 
                        s.unidad_medida, 
                        m.valor, 
                        m.fecha_registro
                    FROM mediciones m
                    JOIN sensores s ON m.sensor_id = s.id
                    JOIN barrios b ON s.barrio_id = b.id
                    WHERE m.fecha_registro IN (
                        SELECT MAX(fecha_registro) 
                        FROM mediciones 
                        GROUP BY sensor_id
                    );
                """)
                return cursor.fetchall()
    
    @staticmethod
    def insertar_alerta(sensor_id: int, valor: float, descripcion: str):
        query = """
            INSERT INTO alertas (sensor_id, valor_disparado, descripcion)
            VALUES (%s, %s, %s) RETURNING id, fecha_alerta;
        """
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (sensor_id, valor, descripcion))
                result = cursor.fetchone()
                conn.commit()
                return {
                    "id": result['id'], 
                    "fecha_alerta": result['fecha_alerta']
                }
    @staticmethod
    def obtener_alertas_recientes():
        """Consulta las últimas 10 alertas críticas en la base de datos."""
        query = """
            SELECT a.id, s.codigo_sensor, a.valor_disparado, a.descripcion, a.fecha_alerta 
            FROM alertas a
            JOIN sensores s ON a.sensor_id = s.id
            ORDER BY a.fecha_alerta DESC LIMIT 10;
        """
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()
    @staticmethod
    def exportar_alertas_por_fecha(fecha_inicio):
        """
        Consulta TODAS las alertas críticas desde una fecha específica
        hasta la actualidad, sin límites, para auditoría externa.
        """
        query = """
            SELECT a.id, s.codigo_sensor, a.valor_disparado, a.descripcion, a.fecha_alerta 
            FROM alertas a
            JOIN sensores s ON a.sensor_id = s.id
            WHERE a.fecha_alerta >= %s
            ORDER BY a.fecha_alerta DESC;
        """
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (fecha_inicio,))
                return cursor.fetchall()