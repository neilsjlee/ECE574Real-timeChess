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
        self.game_lobby_ui = None

        self.in_game_flag = False
        self.mode = ""
        self.my_public_ip = ""
        self.my_private_ip = ""

        self.mqtt_handle = None
        self.am_i_host = True

        self.my_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        self.opponent_id = ""
        self.host_id = ""

        self.MQTT_BROKER_IP = '3.139.21.0'
        self.MQTT_BROKER_PORT = 1883
        self.GAME_LOBBY_DEFAULT_TOPIC = 'game_lobby'
        self.FROM_SERVER = "/from_server"
        self.TO_SERVER = "/to_server"
        self.IN_GAME_DEFAULT_TOPIC = 'in_game'

        self.lock = threading.Lock()

        self.outgoing_message_list = []
        self.outgoing_request_list = []

    def get_control_class(self, control):
        self.c = control
        # self.mode = self.c.mode

    def set_game_lobby_ui_handler(self, game_lobby_ui_handler):
        self.game_lobby_ui = game_lobby_ui_handler

    def p(self):
        self.lock.acquire()

    def v(self):
        self.lock.release()

    def new_movement_message(self, origin, destination, start_time):
        self.p()
        self.outgoing_message_list.append(json.dumps({"origin": list(origin), "destination": list(destination), "start_time": datetime.timestamp(start_time)}))
        self.v()

    def send_movement_message(self):
        if len(self.outgoing_message_list) > 0:
            self.p()
            new_message = self.outgoing_message_list.pop(0)
            self.v()
            self.mqtt_handle.publish(self.IN_GAME_DEFAULT_TOPIC + "/" + self.host_id + "/" + self.mode, new_message)

    def new_request_message(self, request_code, target_host=None):
        if target_host is None:
            payload = {"request": request_code}
        else:
            payload = {"request": request_code, "target_host": target_host}
        self.p()
        self.outgoing_request_list.append(json.dumps(payload))
        self.v()

    def send_request_message(self):
        if len(self.outgoing_request_list) > 0:
            self.p()
            new_message = self.outgoing_request_list.pop(0)
            self.v()
            self.mqtt_handle.publish(self.GAME_LOBBY_DEFAULT_TOPIC + "/" + self.my_id + self.TO_SERVER, new_message)

    def get_my_ip_addresses(self):
        self.my_public_ip = requests.get('https://api.ipify.org').text
        print("My Public IP is ", self.my_public_ip)

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 0))
        self.my_private_ip = s.getsockname()[0]
        s.close()
        print("My Private IP is ", self.my_private_ip)

    def connect(self):
        self.mqtt_handle = mqtt.Client()
        self.mqtt_handle.connect(self.MQTT_BROKER_IP, self.MQTT_BROKER_PORT)

    def send_response(self, response_code, data=None):
        if data is None:
            self.mqtt_handle.publish(self.GAME_LOBBY_DEFAULT_TOPIC + "/" + self.my_id + self.TO_SERVER, json.dumps({"response": response_code}))
        else:
            payload_dict = {"response": response_code}
            payload_dict.update(data)
            self.mqtt_handle.publish(self.GAME_LOBBY_DEFAULT_TOPIC + "/" + self.my_id + self.TO_SERVER, json.dumps(payload_dict))

    def send_request(self, request_code, data=None):
        if data is None:
            self.mqtt_handle.publish(self.GAME_LOBBY_DEFAULT_TOPIC + "/" + self.my_id + self.TO_SERVER, json.dumps({"request": request_code}))
        else:
            payload_dict = {"request": request_code}
            payload_dict.update(data)
            self.mqtt_handle.publish(self.GAME_LOBBY_DEFAULT_TOPIC + "/" + self.my_id + self.TO_SERVER, json.dumps(payload_dict))

    """
    def ready_to_start_a_game(self, mode, opponent_id):
        self.mode = mode
        self.opponent_id = opponent_id
        
        if mode == 'host':
            print("GAME START - START AS A HOST. Opponent ID is: ", self.opponent_id)
            self.send_response("accept_join", {"client_id": self.opponent_id})
            self.host_id = self.my_id
            self.mqtt_handle.subscribe(self.IN_GAME_DEFAULT_TOPIC + "/" + self.host_id + "/client")
            print(self.mode)
            self.in_game_flag = True
            self.game_lobby_ui.start_game()
        elif mode == 'client':
            pass
        """

    def on_message(self, client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

        message_topic_list = msg.topic.split('/')
        message_category = message_topic_list[0]
        data = json.loads(msg.payload.decode())
        if message_category == self.GAME_LOBBY_DEFAULT_TOPIC:
            if "request" in data:
                if data["request"] == "status":  # ACK response to server's status check request
                    self.send_response("ok")
                if data["request"] == "join_request":
                    self.send_response("accept_join", {"client_id": data["client_id"]})
                    self.opponent_id = data["client_id"]
                    print("GAME START - START AS A HOST. Opponent ID is: ", self.opponent_id)
                    self.host_id = self.my_id
                    self.mqtt_handle.subscribe(self.IN_GAME_DEFAULT_TOPIC + "/" + self.host_id + "/client")
                    self.mode = 'host'
                    self.in_game_flag = True

                    self.game_lobby_ui.start_game()

            elif "response" in data:
                if data["response"] == "join_complete":
                    print("GAME START - START AS A CLIENT. Opponent ID is: ", self.opponent_id)
                    self.host_id = self.opponent_id
                    self.mqtt_handle.subscribe(self.IN_GAME_DEFAULT_TOPIC + "/" + self.host_id + "/host")
                    self.mode = 'client'
                    self.in_game_flag = True

                    self.game_lobby_ui.start_game()

                if data["response"] == "ack_fetch_available_hosts":
                    self.game_lobby_ui.update_game_list(data["hosts"])
        elif message_category == self.IN_GAME_DEFAULT_TOPIC:
            if "request" in data:
                if data["request"] == "join":
                    self.opponent_id = data["id"]
                    self.mqtt_handle.publish(self.IN_GAME_DEFAULT_TOPIC + "/" + self.host_id + "/" + self.mode,
                                             json.dumps({"response": "welcome"}))
            if "response" in data:
                if data["response"] == "welcome":
                    self.in_game_flag = True
            elif "origin" in data:
                self.start_new_movement_from_client(tuple(data["origin"]), tuple(data["destination"]),
                                                    datetime.fromtimestamp(data["start_time"]))

    def add_message_listener(self):
        self.mqtt_handle.on_message = self.on_message

    def start_new_movement_from_client(self, origin, destination, start_time):
        target = self.c.find_target(origin)
        if target:
            self.c.start_new_movement_from_network_controller(target, origin, destination, start_time)
        else:
            print("Target piece does not exist")

    def update_user_id(self, new_id):
        self.mqtt_handle.unsubscribe(self.GAME_LOBBY_DEFAULT_TOPIC + "/" + self.my_id + self.FROM_SERVER)
        self.my_id = new_id
        self.mqtt_handle.subscribe(self.GAME_LOBBY_DEFAULT_TOPIC + "/" + self.my_id + self.FROM_SERVER)

    def run(self):
        self.connect()
        self.mqtt_handle.subscribe(self.GAME_LOBBY_DEFAULT_TOPIC)
        self.mqtt_handle.subscribe(self.GAME_LOBBY_DEFAULT_TOPIC + "/" + self.my_id + self.FROM_SERVER)

        self.add_message_listener()

        self.mqtt_handle.loop_start()

        # alive_check_interval = time.time()

        while True:
            """
            if not self.in_game_flag:                       # Game Lobby (Initial Setting)
                if self.mode == "host":
                    self.host_id = self.my_id
                    # self.mqtt_handle.subscribe(self.IN_GAME_DEFAULT_TOPIC + "/" + self.host_id + "/client")
                elif self.mode == "client":
                    pass
                    # self.host_id =
                    # self.in_game_flag = True
                    # self.mqtt_handle.subscribe(self.IN_GAME_DEFAULT_TOPIC + "/" + self.host_id + "/" + ("client" if self.mode == "host" else "host"))
            else:                                           # In Game
                current_time = time.time()
                if current_time - alive_check_interval > 5:
                    alive_check_interval = current_time

                self.send_movement_message()
            self.send_request_message()
            time.sleep(0.1)
            """
            if self.in_game_flag:
                self.send_movement_message()
            self.send_request_message()
            time.sleep(0.1)



