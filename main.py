
import threading
import pygame as pg

from constants import *
from model import Model
from view import View
from control import Control
from network_control import NetworkControl


class Main(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.running = [True]
        self.clock = None
        self.screen = None
        self.m = None
        self.v = None
        self.c = None


    # Override
    def run(self):

        pg.init()
        pg.display.set_caption('Chess')
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.m = Model()
        self.v = View(pg, self.m, self.screen)
        self.c = Control(pg, self.m, self.running)

        network_control = NetworkControl(self.c)
        network_control.start()

        while self.running[0]:
            self.v.view_process()
            self.c.control_process()
            self.m.model_process()

            pg.display.update()
            self.clock.tick(FPS)

        pg.quit()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    main = Main()
    main.start()


