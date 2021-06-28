import os, sys
#sys.path.append('..')
from typing import Optional, Callable

import paho.mqtt.client as mqtt
from common.src.mqtt_message_protocol import Message
import time
import ssl




class MqttClient:
    def __init__(self, device_id: Optional[str]="", client_name: Optional[str] = "", source_q_name=None, host: Optional[str] = "127.0.0.1",
                 port: Optional[int] = 1883, keepalive: Optional[int] = 60, bind_address: Optional[str] = "", secure: Optional[bool] = False):
        self.client = mqtt.Client(client_id=client_name, clean_session=True, userdata=source_q_name, transport="tcp")
        if secure is True:
            port = 1883
            if os.path.exists("/opt/ssl/"):
                self.client.tls_set(ca_certs="/opt/ssl/ca.cert",
                                    certfile="/opt/ssl/{}.crt".format(device_id),
                                    keyfile="/opt/ssl/{}.key".format(device_id),
                                    cert_reqs=ssl.CERT_NONE)
            else:
                # For windows platform and main.py
                self.client.tls_set(ca_certs="ca.cert",
                                    certfile="{}.crt".format(device_id),
                                    keyfile="{}.key".format(device_id),
                                    cert_reqs=ssl.CERT_NONE)
        self.client.connect(host, port, keepalive, bind_address)

    def __del__(self):
        #  self.log.debug("Disconnection from client %s" % self.client._client_id.decode('utf_8'))
        self.client.disconnect()
        self.client.loop_stop()
        time.sleep(0.1)

    def send(self, topic: str, message: object, qos: Optional[int] = 1, retain: Optional[bool] = False):
        if topic is None:
            topic = 'Afron/all'
        if isinstance(message, Message):
            msg = message.toJson()
        else:
            msg = message
        self.client.publish(topic, msg, qos=qos, retain=retain)

    def subscribe(self, on_message_func:  Callable[[object, object, object], None], topic: str, qos: Optional[int] = 1):
        if topic is None:
            topic = 'Afron/#'
        self.client.subscribe(topic, qos)
        self.client.on_message = on_message_func
        self.client.loop_start()

    def get_client_id(self) -> str:
        return self.client.client_id.decode('utf-8')



###############################################################################################
# Testing and use example ONLY
###############################################################################################

def on_test_message(self, client: mqtt.Client, userdata: object, message: Message):
    message_payload = Message().fromByteArray(message.payload)
    print(message_payload)

if __name__ == '__main__':
    log_filename = 'mqtt.log'
    client = MqttClient()
    client.subscribe(on_test_message, "TestTopic")

    tester = MqttClient()
    msg= Message("1", "Key", "This is a test message")
    tester.send("TestTopic", msg)

    time.sleep(5)