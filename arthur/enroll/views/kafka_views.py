from kafka import KafkaProducer
from kafka import KafkaConsumer
from json import loads
import json
import pickle


def kfk(logs):
    producer = KafkaProducer(bootstrap_servers='192.168.79.134:9092',value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    for log in logs:
        producer.send('test', log)
    print("Successful")


#kfk()