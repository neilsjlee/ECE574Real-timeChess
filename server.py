import time
from datetime import datetime
import paho.mqtt.client as mqtt
import json


class Server:
    def __init__(self):
        self.MY_PORT = 1883
        self.MY_IP = '3.139.21.0'
        self.DEFAULT_TOPIC = 'game_lobby'
        self.MY_ID = 'server'

        self.mqtt_handle = None

        self.connected_hosts = []
        self.connected_clients = []

    def connect(self):
        self.mqtt_handle = mqtt.Client(self.MY_ID)
        self.mqtt_handle.connect(self.MY_IP, self.MY_PORT)

    def send_response(self, client_id, response_code, data=None):
        if data is None:
            self.mqtt_handle.publish(self.DEFAULT_TOPIC+"/"+client_id, json.dumps({"response": response_code}))
        else:
            payload_dict = {"response": response_code}
            payload_dict.update(data)
            print(payload_dict)
            self.mqtt_handle.publish(self.DEFAULT_TOPIC + "/" + client_id, json.dumps(payload_dict))

    def send_request(self, client_id, request_code, data=None):
        if data is None:
            self.mqtt_handle.publish(self.DEFAULT_TOPIC+"/"+client_id, json.dumps({"request": request_code}))
        else:
            payload_dict = {"response": request_code}
            self.mqtt_handle.publish(self.DEFAULT_TOPIC + "/" + client_id, json.dumps(payload_dict.update(data)))

    def subscribe(self):
        def on_message(client, userdata, msg):
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

            client_id = msg.topic.split('/')[1]
            data = json.loads(msg.payload.decode())
            if "request" in data:
                if data["request"] == "start_host":
                    print(data["request"])
                    self.send_response(client_id, "ack_start_host")
                    self.connected_hosts.append(client_id)
                    print("Connected Hosts:\t ")
                    for each in self.connected_hosts:
                        print("\t" + each)
                if data["request"] == "start_client":
                    self.send_response(client_id, "ack_start_client", {"hosts": self.connected_hosts})
                    self.connected_clients.append(client_id)

            # print('[ERROR] UNABLE TO PROCESS AN INVALID MESSAGE - Received message is not JSON')

        self.mqtt_handle.subscribe(self.DEFAULT_TOPIC + "/#")
        self.mqtt_handle.on_message = on_message

    def run(self):
        self.connect()
        self.subscribe()
        self.mqtt_handle.loop_start()

        alive_check_interval = time.time()

        while True:
            current_time = time.time()
            if current_time - alive_check_interval > 60:
                print('60 seconds')
                alive_check_interval = current_time
                for each in self.connected_hosts:
                    self.send_request(each, "status")
            time.sleep(0.1)


if __name__ == '__main__':
    server = Server()
    server.run()
