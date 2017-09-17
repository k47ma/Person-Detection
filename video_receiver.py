import pygame
from client import Client
import queue
from PIL import Image
import numpy

# GUI module for displaying video stream


HOST = "10.21.5.196"
PORT = 12345


class VideoReceiver(object):
    def __init__(self):
        object.__init__(self)

        # queue for received images
        self.images = queue.Queue()

        # set up client thread
        self.setup_client()

        # set up GUI
        self.setup_GUI()

    def setup_GUI(self):
        pygame.init()
        screen = pygame.display.set_mode((640, 480))
        clock = pygame.time.Clock()

        while True:
            pressed = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

            try:
                data = self.images.get()
                data = numpy.frombuffer(data)
                img = Image.fromarray(data, 'RGB')
                screen.blit(img, (0, 0))
            except queue.Empty:
                pass

            pygame.display.flip()
            clock.tick(60)

    def setup_client(self):
        global HOST, PORT
        client = Client(HOST, PORT, self.images)
        client.start()

        return client

VideoReceiver()
