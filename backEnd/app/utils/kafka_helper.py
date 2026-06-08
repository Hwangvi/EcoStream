import json
import os
from kafka import KafkaProducer

def crear_productor():
    return KafkaProducer(
        bootstrap_servers=[os.getenv('KAFKA_SERVER', 'ecostream_kafka:29092')],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )