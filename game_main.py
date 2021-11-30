import pygame as pg

from constants import *
from model import Model
from view import View
from control import Control
from datetime import datetime


class GameMain:
    def __init__(self, n_c):

        self.running = [True]
        self.clock = None
        self.screen = None
        self.m = None
        self.v = None
        self.c = None
        self.n_c = n_c

        self.root = None

        self.mode = self.n_c.mode

    # Override
    def run(self):

        pg.init()
        pg.display.set_caption('Chess')
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.m = Model(self.mode)
        self.v = View(pg, self.m, self.screen, self.n_c.host_id, self.n_c.opponent_id if self.mode == 'host' else self.n_c.my_id)
        self.c = Control(pg, self.m, self.n_c, self.running)

        self.n_c.get_control_class(self.c)

        while self.running[0]:
            start_time = datetime.now()
            self.v.view_process()
            self.c.control_process()
            self.m.model_process()

            pg.display.update()
            self.clock.tick(FPS)
            end_time = datetime.now()
            print(end_time - start_time)

        pg.quit()

