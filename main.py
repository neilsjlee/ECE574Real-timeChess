
import threading
import pygame as pg

from model import Model
from view import View
from control import Control
from constants import *


class Main(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.running = True

    # Override
    def run(self):

        pg.init()
        pg.display.set_caption('Chess')
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.m = Model()
        self.v = View(pg, self.m, self.screen)
        self.c = Control(pg, self.m, self.running)

        while self.running:
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


