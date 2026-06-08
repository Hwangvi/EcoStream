import os
import psycopg2
from psycopg2.extras import RealDictCursor, pool
from dotenv import load_dotenv
from contextlib import contextmanager
import sys

load_dotenv()

REQUIRED_ENV_VARS = ["DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD"]
for var in REQUIRED_ENV_VARS:
    if not os.getenv(var):
        print(f"❌ ERROR CRÍTICO: La variable de entorno {var} no está definida.")
        sys.exit(1)

try:
    db_pool = pool.SimpleConnectionPool(
        1, 20,
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", "5432")
    )
    print("✅ Pool de conexiones a PostgreSQL inicializado correctamente.")
except Exception as e:
    print(f"❌ Error al crear el pool de conexiones: {e}")
    sys.exit(1)

def get_db_connection():
    return db_pool.getconn()

def release_db_connection(conn):
    db_pool.putconn(conn)

@contextmanager
def db_cursor():
    conn = get_db_connection()
    cursor = None
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"⚠️ Error en la base de datos: {e}")
        raise e
    finally:
        if cursor:
            cursor.close()
        release_db_connection(conn)

class EcoStreamRepository:
    
    @staticmethod
    def obtener_sensor_id(codigo_sensor: str):
        with db_cursor() as cursor:
            cursor.execute("SELECT id FROM sensores WHERE codigo_sensor = %s", (codigo_sensor,))
            sensor = cursor.fetchone()
            return sensor['id'] if sensor else None

    @staticmethod
    def insertar_medicion(sensor_id: int, valor: float):
        with db_cursor() as cursor:
            cursor.execute(
                "INSERT INTO mediciones (sensor_id, valor) VALUES (%s, %s) RETURNING id, fecha_registro",
                (sensor_id, valor)
            )
            return cursor.fetchone()

    @staticmethod
    def obtener_ultimas_mediciones():
        with db_cursor() as cursor:
            cursor.execute("""
                SELECT s.codigo_sensor, b.nombre as barrio, s.tipo, s.unidad_medida, m.valor, m.fecha_registro
                FROM mediciones m
                JOIN sensores s ON m.sensor_id = s.id
                JOIN barrios b ON s.barrio_id = b.id
                WHERE m.fecha_registro IN (
                    SELECT MAX(fecha_registro) FROM mediciones GROUP BY sensor_id
                );
            """)
            return cursor.fetchall()
    
    @staticmethod
    def insertar_alerta(sensor_id: int, valor: float, descripcion: str):
        with db_cursor() as cursor:
            cursor.execute(
                "INSERT INTO alertas (sensor_id, valor_disparado, descripcion) VALUES (%s, %s, %s) RETURNING id, fecha_alerta, valor_disparado",
                (sensor_id, valor, descripcion)
            )
            return cursor.fetchone()

    @staticmethod
    def obtener_alertas_recientes():
        with db_cursor() as cursor:
            cursor.execute("""
                SELECT a.id, s.codigo_sensor, a.valor_disparado, a.descripcion, a.fecha_alerta 
                FROM alertas a
                JOIN sensores s ON a.sensor_id = s.id
                ORDER BY a.fecha_alerta DESC LIMIT 10;
            """)
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
        with db_cursor() as cursor:
            cursor.execute(query, (fecha_inicio.isoformat(),))
            return cursor.fetchall()
    
    @staticmethod
    def exportar_alertas_por_fecha(fecha_inicio):
        with db_cursor() as cursor:
            cursor.execute("""
                SELECT a.id, s.codigo_sensor, a.valor_disparado, a.descripcion, a.fecha_alerta 
                FROM alertas a
                JOIN sensores s ON a.sensor_id = s.id
                WHERE a.fecha_alerta >= %s
                ORDER BY a.fecha_alerta DESC;
            """, (fecha_inicio,))
            return cursor.fetchall()

    @staticmethod
    def limpiar_alertas():
        with db_cursor() as cursor:
            cursor.execute("TRUNCATE TABLE alertas RESTART IDENTITY;")
    
    @staticmethod
    def purgar_datos_antiguos():
        with db_cursor() as cursor:
            cursor.execute("DELETE FROM mediciones WHERE fecha_registro < NOW() - INTERVAL '7 days';")

    @staticmethod
    def contar_alertas(dias):
        with db_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM alertas WHERE fecha_alerta >= NOW() - INTERVAL '%s days';", (dias,))
            res = cursor.fetchone()
            return res['count'] if res else 0

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
        ORDER BY fecha_evento DESC LIMIT 100;
        """
        with db_cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()