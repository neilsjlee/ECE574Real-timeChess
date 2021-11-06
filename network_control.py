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
    def __init__(self, control):
        threading.Thread.__init__(self)
        self.c = control
        self.mode = self.c.mode
        self.my_public_ip = ""
        self.my_private_ip = ""
        # self.server_socket = None
        self.my_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        self.mqtt = None
        self.am_i_host = True

        self.MQTT_BROKER_IP = '3.139.21.0'
        self.MQTT_BROKER_PORT = 1883

    def start_mqtt_topic_as_host(self):
        self.mqtt = mqtt.Client(self.my_id)
        self.mqtt.connect(self.MQTT_BROKER_IP, self.MQTT_BROKER_PORT)
        # self.mqtt.publish(self.my_id, 'host entered')
        self.mqtt.publish('server', self.my_id)

    def send(self, data):
        self.mqtt.publish()

    def start_new_movement_from_client(self, origin, destination, start_time):
        target = self.c.find_target(origin)
        self.c.start_new_movement(target, origin, destination, start_time)

    def get_my_ip_addresses(self):
        self.my_public_ip = requests.get('https://api.ipify.org').text
        print("My Public IP is ", self.my_public_ip)

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 0))
        self.my_private_ip = s.getsockname()[0]
        s.close()
        print("My Private IP is ", self.my_private_ip)

    '''
    def send_ack_and_setting_socket(self):
        HOST = mobile_app_private_ip
        PORT = 3000

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        data = {
            'public_ip': public_ip,
            'private_ip': private_ip
        }
        data_string = json.dumps(data)
        client_socket.sendall(data_string.encode('utf-8'))
        client_socket.close()

    def socket_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind the socket to a public host, and a well-known port
        self.server_socket.bind((socket.gethostname(), 2121))
        # become a server socket
        self.server_socket.listen(5)
    '''

    def test(self):
        time.sleep(5)
        temp_origin = (1, 1)
        temp_destination = (1, 2)
        self.start_new_movement_from_client(temp_origin, temp_destination, datetime.now())

    def run(self):
        # self.test()

        self.get_my_ip_addresses()

        time.sleep(2)

        '''
        # Test Socket Host
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', self.PORT))
            s.listen()
            connection, address = s.accept()
            with connection:
                print('Connected by', address)
                while True:
                    data = connection.recv(1024)
                    print("received data: ", data, datetime.now())
                    if not data:
                        break
                    connection.sendall(data)
        '''



