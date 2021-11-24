

from constants import *


class View:
    def __init__(self, pg, model, screen, host_id, client_id):
        self.pg = pg
        self.m = model
        self.screen = screen
        self.host_id = host_id
        self.client_id = client_id

        self.pg.freetype.init()
        self.font = pg.freetype.Font('FreeSerif-4aeK.ttf', 50)
        self.micro_font = pg.freetype.Font('FreeSerif-4aeK.ttf', 25)
        self.font2 = pg.font.Font(None, 25)
        self.font3 = pg.freetype.Font('FreeSerif-4aeK.ttf', 50)

    def draw_squares(self):
        color_dict = {True: WHITE, False: MAIZE}
        current_color = True
        for row in range(8):
            for column in range(8):
                self.pg.draw.rect(self.screen, color_dict[current_color], ((BOARD_MARGIN_X + (column * SQUARE_WIDTH)), BOARD_MARGIN_Y + (row * SQUARE_WIDTH), SQUARE_WIDTH, SQUARE_WIDTH))
                current_color = not current_color
            current_color = not current_color

    def draw_names(self):
        self.pg.draw.rect(self.screen, WHITE, (470, 40, 220, 40))
        self.pg.draw.rect(self.screen, WHITE, (470, 400, 220, 40))

        self.micro_font.render_to(self.screen, (480, 50), self.client_id, BLACK)
        self.micro_font.render_to(self.screen, (480, 410), self.host_id, BLACK)

    def draw_pieces(self):
        for row, pieces in enumerate(self.m.board[::(-1 if self.m.player_color_is_black else 1)]):
            for square, piece in enumerate(pieces[::(-1 if self.m.player_color_is_black else 1)]):
                if piece:
                    if piece.cool_down > 0:

                        self.font.render_to(self.screen, (piece.img_adjust[0] + (square * SQUARE_WIDTH), piece.img_adjust[1] + (row * SQUARE_WIDTH)), piece.image, LIGHT_GRAY if piece.color == "white" else DARK_GRAY)

                        text = self.font2.render(str(round(piece.cool_down, 1)), True, ORANGE)
                        text_surface = self.pg.Surface(text.get_size())
                        text_surface.fill(BLACK)
                        text_surface.blit(text, (0, 0))
                        self.screen.blit(text_surface, (BOARD_MARGIN_X + 14 + (square * SQUARE_WIDTH), BOARD_MARGIN_Y + 18 + (row * SQUARE_WIDTH)))


                    else:
                        self.font.render_to(self.screen,
                                            (piece.img_adjust[0] + (square * SQUARE_WIDTH), piece.img_adjust[1] + (row * SQUARE_WIDTH)),
                                            piece.image, BLACK)

    def draw_selected_square(self):
        if self.m.target_square:
            self.pg.draw.rect(self.screen, BLACK, ((BOARD_MARGIN_X + (self.m.true_target[0] * SQUARE_WIDTH)), BOARD_MARGIN_Y + (self.m.true_target[1] * SQUARE_WIDTH), SQUARE_WIDTH, SQUARE_WIDTH), width=2)

    def draw_legal_moves(self):
        for move in self.m.legal_moves:
            if self.m.player_color_is_black:
                self.pg.draw.circle(self.screen, ORANGE, (65 + ((7 - move[0]) * SQUARE_WIDTH), 65 + ((7 - move[1]) * SQUARE_WIDTH)), 5)
            else:
                self.pg.draw.circle(self.screen, ORANGE, (65 + (move[0] * SQUARE_WIDTH), 65 + (move[1] * SQUARE_WIDTH)), 5)

    def draw_moving_piece(self):
        for each in self.m.movement_list:
            self.font.render_to(self.screen, (each['target'].img_adjust[0] + int(each['current_coordinate_x'] * SQUARE_WIDTH),
                                each['target'].img_adjust[1] + int(each['current_coordinate_y'] * SQUARE_WIDTH)), each['target'].image, LIGHT_GRAY if each['target'].color == "white" else DARK_GRAY)

    def view_process(self):
        self.screen.fill(BLUE)          # Background
        self.draw_squares()             # Board
        self.draw_names()
        self.draw_selected_square()
        self.draw_pieces()
        self.draw_moving_piece()
        self.draw_legal_moves()

