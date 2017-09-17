import socket
import threading
import json

# module for client


class Client(object):
    def __init__(self, host, port, queue):
        object.__init__(self)

        self.host = host
        self.port = port
        self.queue = queue

    def start(self):
        s = socket.socket()
        s.connect((self.host, self.port))

        listening_thread = ClientListeningThread(s, self.queue)
        listening_thread.start()

        sending_thread = ClientSendingThread(s)
        sending_thread.start()


class ClientSendingThread(threading.Thread):
    def __init__(self, connection):
        threading.Thread.__init__(self)

        self.connection = connection

    def run(self):
        while True:
            msg = input()
            try:
                self.connection.send(bytes(msg, 'utf-8'))
            except socket.error:
                break


class ClientListeningThread(threading.Thread):
    def __init__(self, connection, queue):
        threading.Thread.__init__(self)

        self.connection = connection
        self.queue = queue

    def run(self):
        while True:
            data = self.connection.recv(100000)
            self.queue.put(data)
