from odoo import models, api
import threading
from confluent_kafka import Consumer, KafkaException, KafkaError
from kafka import KafkaConsumer
import json
from stdnum import me

class KafkaConsumerThread(threading.Thread):
    def __init__(self, env):
        threading.Thread.__init__(self)
        self.env = env
        self.url_kafka_bootstrap_servers = self.env['ir.config_parameter'].sudo().get_param('url_kafka_bootstrap_servers', '192.168.0.171:29092')

    def run(self):
        conf = {
            'bootstrap.servers': self.url_kafka_bootstrap_servers, 
            'group.id': 'odoo_group',               
            'auto.offset.reset': 'earliest',
            'api.version.request': False,
            'log.connection.close': False
        }
        consumer = Consumer(conf)
        consumer.subscribe(['import_db_topic', 'import_dw_topic'])
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(msg.error())
                    break
            try:
                data = json.loads(msg.value().decode('utf-8'))
                message = 'Test'
                if data.get('type', False) == 'db':
                    message = 'Bạn có 1 up bảng đang chờ duyệt.'
                elif data.get('type', False) == 'dw':
                    message = 'Dữ liệu up bảng đã được xử lý thành công và update vào hệ thống.'
                history = self.env['dth.kho.sim.upload.history'].browse(int(data.get('history_id')))
                if history:
                    history.process_message(message)
            except:
                continue
            
        consumer.close()
    
class KafkaConsumerClient(models.Model):
    _name = 'kafka.consumer.client'
    _description = 'Kafka Consumer Client'
    
    def _register_hook(self):
        super(KafkaConsumerClient, self)._register_hook()
        self.start_consumer()

    @api.model
    def start_consumer(self):
        consumer_thread = KafkaConsumerThread(self.env)
        consumer_thread.start()
