
import threading
import pygame as pg
import tkinter as tk

from constants import *
from model import Model
from view import View
from control import Control
from network_control import NetworkControl
from game_lobby_ui import GameLobbyUI


class Main:
    def __init__(self, n_c):

        self.running = [True]
        self.clock = None
        self.screen = None
        self.m = None
        self.v = None
        self.c = None
        self.n_c = n_c

        self.root = None

        self.mode = 'client'

    # Override
    def run(self):

        pg.init()
        pg.display.set_caption('Chess')
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.m = Model(self.mode)
        self.v = View(pg, self.m, self.screen)
        self.c = Control(pg, self.m, self.n_c, self.running)

        self.n_c.get_control_class(self.c)

        while self.running[0]:
            self.v.view_process()
            self.c.control_process()
            self.m.model_process()

            pg.display.update()
            self.clock.tick(FPS)

        pg.quit()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    network_control = NetworkControl()
    network_control.start()
    # main.ui()

    while True:
        game_lobby_ui = GameLobbyUI()
        game_lobby_ui.set_network_control_handler(network_control)
        network_control.set_game_lobby_ui_handler(game_lobby_ui)
        game_lobby_ui.run()

        if True:
            main = Main(network_control)
            main.run()


