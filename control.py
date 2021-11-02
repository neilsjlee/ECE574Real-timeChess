
from constants import *
from datetime import datetime, timedelta
import math


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

    def start_new_movement(self, target, origin, destination, start_time, promotion=None):
        angle = math.atan2((origin[1] - destination[1]), (origin[0] - destination[0]))

        self.m.movement_list.append({"target": target,
                              "origin": origin,
                              "destination": destination,
                              "current_coordinate_x": origin[0],
                              "current_coordinate_y": origin[1],
                              "start_time": start_time,
                              "end_time": start_time + timedelta(seconds=(((((origin[0] - destination[0]) ** 2) + (
                                          (origin[1] - destination[1]) ** 2)) ** (1 / 2)) / PIECE_MOVEMENT_SPEED)/FPS),
                              "angle": angle,
                              "speed_x": - math.cos(angle) * PIECE_MOVEMENT_SPEED,
                              "speed_y": - math.sin(angle) * PIECE_MOVEMENT_SPEED
                              })
        self.m.current_destinations.append((destination[0], destination[1]))
        self.m.legal_moves = []
        self.m.board[origin[1]][origin[0]] = None
        if target.name == 'king':
            if destination[0] - origin[0] == 2:
                self.start_new_movement(self.m.board[target.back_rank][7], (7, target.back_rank), (5, target.back_rank), datetime.now())
            if origin[0] - destination[0] == 2:
                self.start_new_movement(self.m.board[target.back_rank][0], (0, target.back_rank), (3, target.back_rank), datetime.now())


        '''
        if not action:
            action.append([target, destination, promotion])
        elif any((piece[0] == target) and (piece[1] == destination) for piece in action):
            pass
        else:
            [action.remove(item) for item in action if item[0] == target]
            action.append([target, destination, promotion])
        return action
        # print(movement_list)
        '''

    def control_process(self):
        for event in self.pg.event.get():
            if event.type == self.pg.QUIT:
                self.running = False
            if event.type == self.pg.MOUSEBUTTONDOWN:
                if self.m.playing and BOARD_MARGIN_X + SQUARE_WIDTH * 8 >= event.pos[0] >= BOARD_MARGIN_X and BOARD_MARGIN_Y + SQUARE_WIDTH * 8 >= event.pos[1] >= BOARD_MARGIN_Y:
                    if event.button != 3:   # Left mouse button = 1, Mouse Wheel Button = 2, Right mouse button = 3
                        self.m.true_target, self.m.target_square = self.find_square(event.pos[0], event.pos[1])
                        self.m.target = self.m.board[self.m.target_square[1]][self.m.target_square[0]]
                        if self.m.target:
                            # and self.m.target.color == self.m.player_color:
                            self.m.legal_moves = self.m.target.find_moves(self.m.board, self.m.target_square, self.m.current_destinations)
                        else:
                            self.m.target = None
                            self.m.legal_moves = []
                            self.m.target_square = None
                    elif self.m.target_square and self.m.target:    # (i.e. if the right mouse button is pressed,)
                        self.m.true_target, destination = self.find_square(event.pos[0], event.pos[1])
                        if destination in self.m.legal_moves:
                            self.start_new_movement(self.m.target, self.m.target_square, destination, datetime.now())
                        else:
                            pass
                            # self.m.target_square = None
                    else:
                        self.m.target_square = None
