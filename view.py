

from constants import *


class View:
    def __init__(self, pg, model, screen):
        self.pg = pg
        self.m = model
        self.screen = screen

        pg.freetype.init()
        self.font = pg.freetype.Font('FreeSerif-4aeK.ttf', 50)
        self.micro_font = pg.freetype.Font('FreeSerif-4aeK.ttf', 25)

    def draw_squares(self):
        colour_dict = {True: LIGHT, False: DARK}
        current_colour = True
        for row in range(8):
            for column in range(8):
                self.pg.draw.rect(self.screen, colour_dict[current_colour], ((BOARD_MARGIN_X + (column * SQUARE_WIDTH)), BOARD_MARGIN_Y + (row * SQUARE_WIDTH), SQUARE_WIDTH, SQUARE_WIDTH))
                current_colour = not current_colour
            current_colour = not current_colour

    '''
    def draw_coords(self):
        for row in range(8):
            self.font.render_to(self.screen, (10, 45 + (row * 50)), chr(49 + row))
            # self.font.render_to(self.screen, (10, 45 + (row * 50)), chr(56 - row))
        for col in range(8):
            self.font.render_to(self.screen, (45 + (col * 50), 450), chr(72 - col))
            # self.font.render_to(self.screen, (45 + (col * 50), 450), chr(65 + col))
    '''

    def draw_pieces(self, process, delta_x=None, delta_y=None, destination=None):
        ###################modified lines
        if process:
            piece = self.m.board[destination[1]][destination[0]]
            self.font.render_to(self.screen, (piece.img_adjust[0] - delta_x + (destination[0] * 50),
                                piece.img_adjust[1] - delta_y + (destination[1] * 50)), piece.image, SILVER)
        ###################
        else:
            for row, pieces in enumerate(self.m.board[::(-1 if self.m.player_color_is_black else 1)]):
                for square, piece in enumerate(pieces[::(-1 if self.m.player_color_is_black else 1)]):
                    if piece:
                        self.font.render_to(self.screen, (piece.img_adjust[0] + (square * 50), piece.img_adjust[1] + (row * 50)),
                                       piece.image, BLACK)

    def draw_selected_square(self):
        if self.m.target_square:
            self.pg.draw.rect(self.screen, BLACK, ((40 + (self.m.true_target[0] * 50)), 40 + (self.m.true_target[1] * 50), 50, 50), width=2)


    def view_process(self):
        self.screen.fill(GREY)  # Background
        self.draw_squares()     # Board
        # self.draw_coords()
        self.draw_pieces(False)
        self.draw_selected_square()

