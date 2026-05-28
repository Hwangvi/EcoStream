import os
import sys
import json
import redis
from kafka import KafkaConsumer
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.database.database import EcoStreamRepository

load_dotenv()

KAFKA_SERVER = os.getenv('KAFKA_SERVER', 'localhost:9092')
TOPIC_NAME = 'telemetria-sensores'

r = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

UMBRALES = {
    "CO2": 450.0,
    "RUIDO": 75.0,
    "TRAFICO": 35.0
}

try:
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=[KAFKA_SERVER],
        auto_offset_reset='latest',
        enable_auto_commit=True,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    print(f"🎧 Escuchando eventos y gestionando alertas en tiempo real...")
except Exception as e:
    print(f"❌ Error al conectar con Kafka: {e}")
    exit(1)

try:
    for message in consumer:
        datos = message.value
        codigo_sensor = datos.get("codigo_sensor")
        valor = datos.get("valor")
        
        print(f"📩 Evento desde Kafka: Sensor={codigo_sensor} | Valor={valor}")
        
        try:
            redis_key = f"sensor:{codigo_sensor}"
            r.hset(redis_key, mapping={
                "valor": valor, 
                "codigo_sensor": codigo_sensor,
                "unidad_medida": "ppm" if "CO2" in codigo_sensor else "dB" if "RUIDO" in codigo_sensor else "vehiculos/min"
            })
            print(f"⚡ [Redis] Caché actualizada para {codigo_sensor}")
            
            sensor_id = EcoStreamRepository.obtener_sensor_id(codigo_sensor)
            if sensor_id:
                nuevo_registro = EcoStreamRepository.insertar_medicion(sensor_id, valor)
                print(f"💾 [PostgreSQL] Histórico guardado. ID: {nuevo_registro['id']}")
                
                tipo_sensor = codigo_sensor.split("-")[-1] 
                
                if tipo_sensor in UMBRALES and valor > UMBRALES[tipo_sensor]:
                    zona = codigo_sensor.split("-")[1]
                    descripcion_alerta = f"Alerta de {tipo_sensor} detectada en zona {zona}. Límite seguro superado."
                    valor_a_guardar = float(valor)
                    nueva_alerta = EcoStreamRepository.insertar_alerta(sensor_id, valor, descripcion_alerta)
                    print(f"🚨 [ALERTA CRÍTICA] {descripcion_alerta} | Valor: {valor} | ID Alerta: {nueva_alerta['id']}")
            
        except Exception as err:
            print(f"❌ Error al procesar datos del evento: {err}")
            
        print("." * 40)

except KeyboardInterrupt:
    print("\n🛑 Consumidor detenido manualmente por el usuario.")
finally:
    if 'consumer' in locals():
        consumer.close()
        print("🔌 Conexión con Kafka cerrada limpiamente.")