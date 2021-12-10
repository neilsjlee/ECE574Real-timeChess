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

        pg.init()                           # PyGame Init
        pg.display.set_caption('Chess')
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.m = Model(self.mode)
        self.v = View(pg, self.m, self.screen, self.n_c.host_id, self.n_c.opponent_id if self.mode == 'host' else self.n_c.my_id)
        self.c = Control(pg, self.m, self.n_c, self.running)

        self.n_c.get_control_class(self.c)

        while self.running[0]:
            # Round Robin Scheduling
            self.v.view_process()       # View class process
            self.c.control_process()    # Control class process
            self.m.model_process()      # Model class process

            pg.display.update()         # Refresh PyGame Display
            self.clock.tick(FPS)    # FPS = 60

        pg.quit()

