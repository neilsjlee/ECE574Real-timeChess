
import threading
import pygame as pg
import tkinter as tk
import json

from constants import *
from model import Model
from view import View
from control import Control
from network_control import NetworkControl


class Main(threading.Thread):
    def __init__(self, n_c):
        threading.Thread.__init__(self)

        self.running = [True]
        self.clock = None
        self.screen = None
        self.m = None
        self.v = None
        self.c = None
        self.n_c = n_c

        self.root = None

        self.mode = ''

    def ui(self):
        self.root = tk.Tk()
        self.root.title("Real-time Chess Client Program")

        main_frame = tk.Frame(self.root)
        main_frame.grid(row=0, column=0)

        btn_host = tk.Button(main_frame, text="Host", width=50, height=20, command=self.host_button)
        btn_host.grid(row=0, column=0)

        btn_client = tk.Button(main_frame, text="Client", width=50, height=20, command=self.client_button)
        btn_client.grid(row=0, column=1)

        self.root.pack_propagate(0)
        self.root.mainloop()

    def host_button(self):
        self.mode = 'host'
        self.n_c.mode = self.mode
        self.n_c.new_request_message("start_host")
        self.root.destroy()

    def client_button(self):
        self.mode = 'client'
        self.n_c.mode = self.mode
        self.n_c.new_request_message("start_client")
        self.root.destroy()

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
    main = Main(network_control)
    main.ui()
    if main.mode == 'host' or main.mode == 'client':
        main.start()

