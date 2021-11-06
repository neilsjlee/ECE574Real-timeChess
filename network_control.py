import threading
import time
from datetime import datetime
import requests
import socket
import paho.mqtt.client as mqtt
import random
import string
import json


class NetworkControl(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.c = None
        self.mode = ""
        self.my_public_ip = ""
        self.my_private_ip = ""

        self.mqtt_handle = None
        self.am_i_host = True

        self.my_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        self.opponent_id = ""

        self.MQTT_BROKER_IP = '3.139.21.0'
        self.MQTT_BROKER_PORT = 1883
        self.GAME_LOBBY_DEFAULT_TOPIC = 'game_lobby'
        self.IN_GAME_DEFAULT_TOPIC = 'in_game'

        self.lock = threading.Lock()

        self.outgoing_message_list = []
        self.outgoing_request_list = []

    def get_control_class(self, control):
        self.c = control
        self.mode = self.c.mode

    def p(self):
        self.lock.acquire()

    def v(self):
        self.lock.release()

    def new_movement_message(self, origin, destination, start_time):
        self.p()
        self.outgoing_message_list.append([origin, destination, start_time])
        self.v()

    def send_movement_message(self):
        if len(self.outgoing_message_list) > 0:
            self.p()
            new_message = self.outgoing_message_list.pop(0)
            self.v()
            self.mqtt_handle.publish(json.dumps({"origin": new_message[0], "destination": new_message[1], "start_time": new_message[2]}))

    def send_request_message(self):
        if len(self.outgoing_request_list) > 0:
            new_message = self.outgoing_request_list.pop(0)
            self.mqtt_handle.publish(json.dumps({"origin": new_message[0], "destination": new_message[1], "start_time": new_message[2]}))

    def get_my_ip_addresses(self):
        self.my_public_ip = requests.get('https://api.ipify.org').text
        print("My Public IP is ", self.my_public_ip)

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 0))
        self.my_private_ip = s.getsockname()[0]
        s.close()
        print("My Private IP is ", self.my_private_ip)

    def connect(self):
        self.mqtt_handle = mqtt.Client(self.my_id)
        self.mqtt_handle.connect(self.MQTT_BROKER_IP, self.MQTT_BROKER_PORT)

    def send_response(self, client_id, response_code, data=None):
        if data is None:
            self.mqtt_handle.publish(self.GAME_LOBBY_DEFAULT_TOPIC + "/" + client_id, json.dumps({"response": response_code}))
        else:
            payload_dict = {"response": response_code}
            payload_dict.update(data)
            print(payload_dict)
            self.mqtt_handle.publish(self.GAME_LOBBY_DEFAULT_TOPIC + "/" + client_id, json.dumps(payload_dict))

    def send_request(self, request_code, data=None):
        if data is None:
            self.mqtt_handle.publish(self.GAME_LOBBY_DEFAULT_TOPIC + "/" + self.my_id, json.dumps({"request": request_code}))
        else:
            payload_dict = {"response": request_code}
            self.mqtt_handle.publish(self.GAME_LOBBY_DEFAULT_TOPIC + "/" + self.my_id, json.dumps(payload_dict.update(data)))

    def add_message_listener(self):
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

        self.mqtt_handle.on_message = on_message

    def start_new_movement_from_client(self, origin, destination, start_time):
        target = self.c.find_target(origin)
        if target:
            self.c.start_new_movement_from_network_controller(target, origin, destination, start_time)
        else:
            print("Target piece does not exist")

    def test(self):
        temp_origin = (1, 1)
        temp_destination = (1, 2)
        self.start_new_movement_from_client(temp_origin, temp_destination, datetime.now())

    def run(self):
        self.connect()
        self.mqtt_handle.subscribe(self.GAME_LOBBY_DEFAULT_TOPIC + "/#")

        self.mqtt_handle.loop_start()

        alive_check_interval = time.time()

        while True:
            current_time = time.time()
            if current_time - alive_check_interval > 5:
                self.test()
                alive_check_interval = current_time

            self.send_movement_message()

            time.sleep(0.1)



