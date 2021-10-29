
from constants import *


class Control:

    def __init__(self, pg, model, running):
        self.pg = pg
        self.m = model
        self.running = running


    def find_square(self, x, y):
        true_target = int((x - BOARD_MARGIN_X) / SQUARE_WIDTH), int((y - BOARD_MARGIN_Y) / SQUARE_WIDTH)
        if self.m.player_color_is_black:
            target_square = 7 - true_target[0], 7 - true_target[1]
        else:
            target_square = true_target
        return true_target, target_square

    def control_process(self):
        for event in self.pg.event.get():
            if event.type == self.pg.QUIT:
                self.running = False
            if event.type == self.pg.MOUSEBUTTONDOWN:
                if self.m.playing and BOARD_MARGIN_X + SQUARE_WIDTH * 8 >= event.pos[0] >= BOARD_MARGIN_X and BOARD_MARGIN_Y + SQUARE_WIDTH * 8 >= event.pos[1] >= BOARD_MARGIN_Y:
                    if event.button != 3:   # Left mouse button = 1, Mouse Wheel Button = 2, Right mouse button = 3
                        self.m.true_target, self.m.target_square = self.find_square(event.pos[0], event.pos[1])
                        self.m.target = self.m.board[self.m.target_square[1]][self.m.target_square[0]]
                        # if target and self.m.player_color_is_black == target.colour:
                        if self.m.target:
                            # Modified above 1 line(s)
                            self.m.legal_moves = self.m.target.find_moves(self.m.board, self.m.target_square)
                    elif self.m.target_square and self.m.target:
                        self.m.true_target, destination = self.find_square(event.pos[0], event.pos[1])
                        if destination in self.m.legal_moves:
                            action_list = start_new_movement(board, target, target_square, destination, datetime.now(),
                                                             action_list, promotion)
                            board, captures, kings, check = move_piece(board, target, kings, target_square, destination,
                                                                       captures, promotion)

                            legal_moves = []
                        else:
                            target_square = None
                    else:
                        target_square = None