
from constants import *
from datetime import datetime


class Model:

    def __init__(self, mode):
        self.board = self.reset_board()
        self.playing = True
        self.mode = mode

        self.player_color_is_black = False
        self.player_color = 'white' if self.mode == 'host' else 'black'

        self.target_square = None
        self.target = None
        self.true_target = None
        self.legal_moves = []
        self.movement_list = []
        self.current_destinations = []
        self.captures = []
        self.cool_down_list = []

        self.promotion = 'queen'

    def reset_board(with_pieces=True):
        def generate_pieces(color):
            return [Rook(color), Knight(color), Bishop(color), Queen(color),
                    King(color), Bishop(color), Knight(color), Rook(color)]

        board = [[None for x in range(8)] for x in range(8)]
        if with_pieces:
            board[0] = generate_pieces("black")
            board[7] = generate_pieces("white")
            board[1] = [Pawn("black") for square in board[1]]
            board[6] = [Pawn("white") for square in board[6]]
        return board

    def process_movement(self):
        for each in self.movement_list:
            if ((abs(each['current_coordinate_y'] - each['destination'][1]) < 0.01) & (
                    abs(each['current_coordinate_x'] - each['destination'][0]) < 0.01)) or each['end_time'] < datetime.now():
                self.movement_list.remove(each)
                # self.current_destinations.remove((each['destination'][0], each['destination'][1]))
                self.complete_movement(each['target'], each['origin'], each['destination'])
                break
            else:
                each['current_coordinate_x'] += each['speed_x']
                each['current_coordinate_y'] += each['speed_y']

    def complete_movement(self, target, origin, destination):
        try:
            self.current_destinations.remove(destination)
        except:
            pass

        # piece move conditions
        # for row in self.board:
#             for piece in row:
#                 if piece and piece.name == 'pawn' and piece.en_passant:
#                     piece.en_passant = False

        if target.name == 'pawn':
            if target.double_move:
                target.double_move = False
            if abs(origin[1] - destination[1]) == 2:
                target.en_passant = True
            else:
                target.en_passant = False
            if origin[0] != destination[0] and not self.board[destination[1]][destination[0]]:
                self.captures.append(self.board[destination[1] - target.direction][destination[0]])
                # print(captures)
                # print([destination[1] - target.direction][destination[0]])
                self.board[destination[1] - target.direction][destination[0]] = None
            if destination[1] == (0 if target.color == 'white' else 7):
                promoting = True
                piece_dict = {'queen': Queen(target.color), 'knight': Knight(target.color),
                              'rook': Rook(target.color), 'bishop': Bishop(target.color)}
                target = Queen(target.color)
        if target.name == 'king':
            # kings[int(target.color == "black")] = destination
            if target.castle_rights:
                target.castle_rights = False
            if destination[0] - origin[0] == 2:
                self.board[target.back_rank][5] = self.board[target.back_rank][7]
                self.board[target.back_rank][7] = None
            if origin[0] - destination[0] == 2:
                self.board[target.back_rank][3] = self.board[target.back_rank][0]
                self.board[target.back_rank][0] = None
        if target.name == 'rook' and target.castle_rights:
            target.castle_rights = False

        # add any existing piece to captures list
        if self.board[destination[1]][destination[0]]:
            self.captures.append(self.board[destination[1]][destination[0]])

        self.board[destination[1]][destination[0]] = target

        # move piece
        # if not promoting:
        #     board[destination[1]][destination[0]] = target
        # else:
        #     board[destination[1]][destination[0]] = piece_dict[promotion]
        #     transcript = transcript[:-1] + f'={promotion[0].upper()} ' if promotion != 'knight' else '=N '
        # self.board[origin[1]][origin[0]] = None

        # any checks with new board status
        # enemy_king = kings[int(target.color == "white")]
        # check = board[enemy_king[1]][enemy_king[0]].in_check(board, enemy_king)
        # return board, captures, kings, check
        target.cool_down = COOL_DOWN
        self.cool_down_list.append(target)

    def process_cool_down(self):
        for each in self.cool_down_list:
            each.cool_down -= PIECE_MOVEMENT_SPEED
            if each.cool_down <= 0:
                each.cool_down = 0
                self.cool_down_list.remove(each)
                if each.name == 'pawn':
                    each.en_passant = False

    def model_process(self):
        self.process_movement()
        self.process_cool_down()


class Piece:
    images = ['white_king', 'white_queen', 'white_rook', 'white_bishop', 'white_knight', 'white_pawn', 'black_king',
              'black_queen', 'black_rook', 'black_bishop', 'black_knight', 'black_pawn']

    def __init__(self, color, name, img_adjust=(50, 50), unbounded=True):
        self.color = color
        self.name = name
        self.image = chr(int('98' + str(self.images.index(f'{color}_{name}') + 12)))
        self.img_adjust = img_adjust
        self.unbounded = unbounded
        self.cool_down = 0

    def find_moves(self, board, location, current_destinations):
        x, y = location[0], location[1]
        legal_moves = []
        additional = set()
        if self.name == 'pawn':
            additional.update(self.additional_moves(board, x, y))
        for x2, y2 in self.moveset.union(additional):
            if any(i < 0 for i in (x + x2, y + y2)):
                continue
            try:
                coords = x + x2, y + y2
                square = board[coords[1]][coords[0]]
                if self.name != 'pawn' and ((square is None or (square and square.color != self.color)) and ((coords[0], coords[1]) not in current_destinations)) \
                        or self.name == 'pawn' and ((x2 == 0 and square is None) or (x2, y2) in additional):
                    legal_moves.append(coords)
                    if square and square.color != self.color or coords not in legal_moves:
                        continue
                    while self.unbounded or self.name == 'pawn' and self.double_move:
                        coords = coords[0] + x2, coords[1] + y2
                        square = board[coords[1]][coords[0]]
                        if all(i >= 0 for i in coords) and self.name != 'pawn' and ((square is None or (square and square.color != self.color)) and ((coords[0], coords[1]) not in current_destinations)) or self.name == 'pawn' and (
                                x2 == 0 and square is None):
                            legal_moves.append(coords)
                        else:
                            break
                        if self.name == 'pawn' or square and square.color != self.color or ((coords[0], coords[1]) in current_destinations):
                            break
            except IndexError:
                continue
        if self.name == 'king' and self.castle_rights and self.castle(board, x, y):
            legal_moves.extend(self.castle(board, x, y))
        return legal_moves


class King(Piece):
    def __init__(self, color):
        self.back_rank = 7 if color == 'white' else 0
        self.moveset = {(x, y) for x in range(-1, 2) for y in range(-1, 2) if x != 0 or y != 0}
        self.castle_rights = True
        super().__init__(color, 'king', unbounded=False)

    def in_check(self, board, location, moved_from=None, moved_to=None):
        for move in self.moveset:
            coords = location
            square = board[coords[1]][coords[0]]
            while (coords != moved_to or location == moved_to) and (
                    coords == location or coords == moved_from or square is None):
                try:
                    if any(i < 0 or i > 7 for i in (coords[0] + move[0], coords[1] + move[1])):
                        break
                    coords = coords[0] + move[0], coords[1] + move[1]
                    square = board[coords[1]][coords[0]]
                except IndexError:
                    break
            if square is None or square.color == self.color or coords == moved_to:
                continue
            if 0 in move and (square.name == 'rook' or square.name == 'queen') or 0 not in move and (
                    square.name == 'bishop' or square.name == 'queen' or (square.name == 'pawn' and
                                                                          location[1] - coords[1] == square.direction)):
                return True
        for x, y in {(x, y) for x in range(-2, 3) for y in range(-2, 3) if x != 0 and y != 0 and abs(x) != abs(y)}:
            try:
                coords = location[0] + x, location[1] + y
                square = board[coords[1]][coords[0]]
                if any(i < 0 for i in (coords[0], coords[1])):
                    continue
                if square and square.color != self.color and square.name == 'knight' and coords != moved_to:
                    return True
            except IndexError:
                continue
        return False

    def castle(self, board, x, y):
        moves = []
        if board[self.back_rank][0] and board[self.back_rank][0].name == 'rook' and board[self.back_rank][
            0].castle_rights:
            squares = [(i, self.back_rank) for i in range(1, 4)]
            if all(not piece for piece in board[self.back_rank][1:4]) and all(
                    not self.in_check(board, square) for square in squares):
                moves.append((2, self.back_rank))
        if board[self.back_rank][7] and board[self.back_rank][7].name == 'rook' and board[self.back_rank][
            7].castle_rights:
            squares = [(i, self.back_rank) for i in range(5, 7)]
            if all(not piece for piece in board[self.back_rank][5:7]) and all(
                    not self.in_check(board, square) for square in squares):
                moves.append((6, self.back_rank))
        return moves


class Queen(Piece):
    def __init__(self, color):
        self.moveset = {(x, y) for x in range(-1, 2) for y in range(-1, 2) if x != 0 or y != 0}
        super().__init__(color, 'queen', img_adjust=(47, 50))


class Rook(Piece):
    def __init__(self, color):
        self.moveset = {(x, y) for x in range(-1, 2) for y in range(-1, 2) if (x == 0 or y == 0) and (x != 0 or y != 0)}
        self.castle_rights = True
        super().__init__(color, 'rook', img_adjust=(52, 53))


class Bishop(Piece):
    def __init__(self, color):
        self.moveset = {(x, y) for x in range(-1, 2) for y in range(-1, 2) if x != 0 and y != 0}
        super().__init__(color, 'bishop', img_adjust=(49, 49))


class Knight(Piece):
    def __init__(self, color):
        self.moveset = {(x, y) for x in range(-2, 3) for y in range(-2, 3) if x != 0 and y != 0 and abs(x) != abs(y)}
        super().__init__(color, 'knight', img_adjust=(50, 52), unbounded=False)


class Pawn(Piece):
    def __init__(self, color):
        self.direction = -1 if color == 'white' else 1
        self.moveset = {(0, y * self.direction) for y in range(1, 2)}
        self.en_passant = False
        self.double_move = True
        super().__init__(color, 'pawn', img_adjust=(54, 52), unbounded=False)

    def additional_moves(self, board, x, y):
        valid_attacks = set()
        for n in range(-1, 2, 2):
            try:
                square = board[y + self.direction][x + n]
                if square and square.color != self.color:
                    valid_attacks.add((n, self.direction))
                else:
                    square = board[y][x + n]
                    if square and square.name == 'pawn' and square.color != self.color and square.en_passant:
                        valid_attacks.add((n, self.direction))
            except IndexError:
                pass
        return valid_attacks
