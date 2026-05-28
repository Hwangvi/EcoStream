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
            VALUES (%s, %s, %s) 
            RETURNING id, fecha_alerta, valor_disparado;
        """
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (sensor_id, valor, descripcion))
                result = cursor.fetchone()
                conn.commit()
                return result
    @staticmethod
    def obtener_alertas_recientes():
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
    def obtener_datos_auditoria_unificados(fecha_inicio):
        query = """
        SELECT * FROM (
            SELECT 'MEDICION' as tipo, m.fecha_registro as fecha_evento, s.codigo_sensor, m.valor::DECIMAL(10,2) as valor, 'Promedio operacional' as descripcion
            FROM mediciones m JOIN sensores s ON m.sensor_id = s.id
            UNION ALL
            SELECT 'ALERTA' as tipo, a.fecha_alerta as fecha_evento, s.codigo_sensor, a.valor_disparado::DECIMAL(10,2) as valor, a.descripcion
            FROM alertas a JOIN sensores s ON a.sensor_id = s.id
        ) as union_tabla
        WHERE fecha_evento >= %s
        ORDER BY fecha_evento DESC;
        """
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
    
                fecha_str = fecha_inicio.isoformat()
                cursor.execute(query, (fecha_str,)) 
                return cursor.fetchall()
    
    @staticmethod
    def exportar_alertas_por_fecha(fecha_inicio):
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
    @staticmethod
    def limpiar_alertas():
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("TRUNCATE TABLE alertas RESTART IDENTITY;")
                conn.commit()
    
    @staticmethod
    def purgar_datos_antiguos():
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM mediciones WHERE fecha_registro < NOW() - INTERVAL '7 days';")
                conn.commit()
    

    @staticmethod
    def contar_alertas(dias):
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM alertas WHERE fecha_alerta >= NOW() - INTERVAL '%s days';", 
                    (dias,)
                )
                return cursor.fetchone()[0]
    @staticmethod
    def obtener_ultimas_100_filas():
        query = """
        SELECT * FROM (
            SELECT 'MEDICION' as tipo, m.fecha_registro as fecha_evento, s.codigo_sensor, m.valor::DECIMAL(10,2) as valor, 'Promedio operacional' as descripcion
            FROM mediciones m JOIN sensores s ON m.sensor_id = s.id
            UNION ALL
            SELECT 'ALERTA' as tipo, a.fecha_alerta as fecha_evento, s.codigo_sensor, a.valor_disparado::DECIMAL(10,2) as valor, a.descripcion
            FROM alertas a JOIN sensores s ON a.sensor_id = s.id
        ) as union_tabla
        ORDER BY fecha_evento DESC
        LIMIT 100;
        """
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()