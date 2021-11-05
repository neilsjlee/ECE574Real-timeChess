import paho.mqtt.client as mqtt
import json


class Server:
    def __init__(self):
        self.MY_PORT = 1883
        self.MY_IP = '3.139.21.0'
        self.DEFAULT_TOPIC = '/server'
        self.MY_ID = 'server'

        self.client = None

        self.connected_hosts = []
        self.connected_clients = []

    def connect(self):
        self.client = mqtt.Client(self.MY_ID)
        self.client.connect(self.MY_IP, self.MY_PORT)

    def subscribe(self):
        def on_message(client, userdata, msg):
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

            try:
                print(json.loads(msg.payload.decode()))
            except:
                print('[ERROR] UNABLE TO PROCESS AN INVALID MESSAGE - Received message is not JSON')

        self.client.subscribe(self.DEFAULT_TOPIC)
        self.client.on_message = on_message

    def run(self):
        self.connect()
        self.subscribe()
        self.client.loop_forever()

        while True:
            pass


if __name__ == '__main__':
    server = Server()
    server.run()
