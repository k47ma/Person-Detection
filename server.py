import socket
import threading
import time
import json
import cv2

# module for server on the car


vc = cv2.VideoCapture(0)


class Server(object):
    def __init__(self, port):
        object.__init__(self)

        self.HOST = socket.gethostbyname(socket.gethostname())
        self.PORT = port

    def start(self):
        s = socket.socket()
        s.bind((self.HOST, self.PORT))

        print("Server is listening to port " + str(self.PORT) + " at " + self.HOST)

        s.listen(5)
        print("Waiting for connection...")

        while True:
            client, addr = s.accept()
            print("New connection from " + addr[0] + " - " + str(addr[1]))

            listening_thread = ServerListeningThread(self, client, addr)
            listening_thread.start()

            sending_thread = ServerSendingThread(client)
            sending_thread.start()


class ServerListeningThread(threading.Thread):
    def __init__(self, server, client, client_info):
        threading.Thread.__init__(self)

        self.server = server
        self.client = client
        self.client_info = client_info

    def run(self):
        while True:
            try:
                data = self.client.recv(1024)
                print(data)
            except socket.error:
                print(self.client_info[0] + "-" + str(self.client_info[1]))
                break


class ServerSendingThread(threading.Thread):
    def __init__(self, client):
        threading.Thread.__init__(self)

        self.client = client

    def run(self):
        global vc

        while True:
            result, image = vc.read()
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.resize(image, (640, 480))

            self.client.send(image)
            time.sleep(1)

Server(12345).start()
