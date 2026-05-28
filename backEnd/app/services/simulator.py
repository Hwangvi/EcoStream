import time
import random
import json
import os
from kafka import KafkaProducer
from dotenv import load_dotenv

load_dotenv()

KAFKA_SERVER = os.getenv('KAFKA_SERVER', 'localhost:9092')
TOPIC_NAME = 'telemetria-sensores'

try:
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_SERVER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    print("✅ Conectado exitosamente a Apache Kafka.")
except Exception as e:
    print(f"❌ Error al conectar con Kafka: {e}")
    exit(1)

SENSORES = [
    {"codigo": "SEN-CENTRO-CO2", "base": 400, "variacion": 30},
    {"codigo": "SEN-CENTRO-RUIDO", "base": 60, "variacion": 10},
    {"codigo": "SEN-NORTE-TRAFICO", "base": 20, "variacion": 10},
    {"codigo": "SEN-SUR-CO2", "base": 400, "variacion": 30}
]

print(f"Simulador EcoStream (PRODUCER) enviando datos al topic '{TOPIC_NAME}' cada 3 segundos...\n")

try:
    while True:
        for sensor in SENSORES:
            valor_simulado = round(sensor["base"] + random.uniform(-sensor["variacion"], sensor["variacion"]), 2)
            if valor_simulado < 0: valor_simulado = 0
            
            payload = {
                "codigo_sensor": sensor["codigo"],
                "valor": valor_simulado
            }
            
            producer.send(TOPIC_NAME, value=payload)
            print(f"[Kafka Stream] Enviado -> {sensor['codigo']}: {valor_simulado}")
            
        print("-" * 50)
        time.sleep(3)

except KeyboardInterrupt:
    print("\n🛑 Simulador detenido.")
finally:
    producer.flush() 
    producer.close()