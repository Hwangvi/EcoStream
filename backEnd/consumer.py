import os
import json
import redis
from kafka import KafkaConsumer
from database import EcoStreamRepository
from dotenv import load_dotenv

load_dotenv()

KAFKA_SERVER = os.getenv('KAFKA_SERVER', 'localhost:9092')
TOPIC_NAME = 'telemetria-sensores'

r = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

print("📥 Iniciando Consumidor EcoStream con soporte para Redis...")

try:
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=[KAFKA_SERVER],
        auto_offset_reset='latest',
        enable_auto_commit=True,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    print(f"🎧 Escuchando eventos y actualizando caché en tiempo real...")
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
                "codigo_sensor": codigo_sensor
            })
            print(f"⚡ [Redis] Caché actualizada para {codigo_sensor}")

            sensor_id = EcoStreamRepository.obtener_sensor_id(codigo_sensor)
            if sensor_id:
                nuevo_registro = EcoStreamRepository.insertar_medicion(sensor_id, valor)
                print(f"💾 [PostgreSQL] Histórico guardado. ID: {nuevo_registro['id']}")
            
        except Exception as err:
            print(f"❌ Error al procesar datos: {err}")
            
        print("." * 30)

except KeyboardInterrupt:
    print("\n🛑 Consumidor detenido.")
finally:
    consumer.close()