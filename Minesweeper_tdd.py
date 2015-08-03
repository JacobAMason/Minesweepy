# coding=utf-8
import random

__author__ = 'JacobAMason'


class Board:
    alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l",
                "m",
                "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y",
                "z"]

    class Tile:
        def __init__(self, x, y):
            self.position = (x, y)
            self.nearbyMines = 0
            self.isMine = False
            self.isHidden = True
            self.isFlagged = False

        def __repr__(self):
            if not self.isHidden and self.isMine:
                if self.isFlagged:
                    return "/ "
                else:
                    return "X "

            if self.isFlagged:
                return "▓▓"
            elif self.isHidden:
                return "██"
            elif self.nearbyMines == 0:
                return "  "
            else:
                return str(self.nearbyMines) + " "

        def set_as_mine(self):
            self.isMine = True

        def set_number_of_nearby_mines(self, number):
            self.nearbyMines = number

        def reveal(self):
            self.isHidden = False

        def toggle_flag(self):
            self.isFlagged = not self.isFlagged
            return self.isFlagged

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.is_mine_triggered = False
        self.initialize_grid()
        self.number_of_flags = 0

    def initialize_grid(self):
        self.minePositions = []
        self.grid = [
            [Board.Tile(x, y) for x in range(self.width)] for y in
            range(self.height)]

    def place_mines(self, numberOfMinesToPlace, tileToAvoid):
        for i in range(numberOfMinesToPlace):
            tile = self.pick_random_unused_mine_position(tileToAvoid)
            tile.set_as_mine()
            self.increment_tiles_around_mine(tile)
            self.minePositions.append(tile)

    def pick_random_unused_mine_position(self, tileToAvoid):
        tile = self.pick_random_tile()
        while tile in self.minePositions or tile is tileToAvoid:
            tile = self.pick_random_tile()
        return tile

    def pick_random_tile(self):
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)
        return self.convert_coordinate_to_tile(x, y)

    def increment_tiles_around_mine(self, centerTile):
        for tile in self.surrounding_tiles(centerTile):
            tile.nearbyMines += 1

    def toggle_flag(self, x, y):
        if self.is_valid_coordinate(x, y):
            if (self.convert_coordinate_to_tile(x, y).toggle_flag()):
                self.number_of_flags += 1
            else:
                self.number_of_flags -= 1

    def reveal(self, x, y):
        if self.is_valid_coordinate(x, y):
            tile = self.convert_coordinate_to_tile(x, y)
            if not tile.isFlagged:
                tile.reveal()
                if tile.nearbyMines == 0:
                    self.reveal_surrounding_tiles(tile)
            if tile.isMine:
                self.game_loss()

    def reveal_surrounding_tiles(self, centerTile):
        for tile in self.surrounding_tiles(centerTile):
            if tile.isHidden and not tile.isFlagged:
                tile.reveal()

    def surrounding_tiles(self, tile):
        x, y = tile.position
        surroundingPositions = [(x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
                                (x - 1, y), (x + 1, y), (x - 1, y + 1),
                                (x, y + 1), (x + 1, y + 1)]
        for x, y in surroundingPositions:
            if self.is_valid_coordinate(x, y):
                yield self.convert_coordinate_to_tile(x, y)

    def convert_coordinate_to_tile(self, x, y):
        return self.grid[y][x]

    def is_valid_coordinate(self, x, y):
        return x in range(self.width) and y in range(self.height)

    def game_loss(self):
        self.is_mine_triggered = True
        self.reveal_whole_board()

    def reveal_whole_board(self):
        for row in self.grid:
            for tile in row:
                tile.reveal()

    def __repr__(self):
        rtnString = self.column_markers()
        rtnString += self.inner_board()
        rtnString += self.column_markers()
        return rtnString

    def column_markers(self):
        return "  " + " ".join(Board.alphabet[:self.width]) + "\n"

    def inner_board(self):
        rtnString = ""
        for rowNumber, row in enumerate(self.grid):
            rtnString += self.inner_board_start_row_marker(rowNumber)
            rtnString += self.inner_board_row_tiles(row)
            rtnString += self.inner_board_end_row_marker(rowNumber)
        return rtnString

    def inner_board_row_tiles(self, row):
        rtnString = ""
        for tile in row:
            rtnString += str(tile)
        return rtnString

    def inner_board_start_row_marker(self, rowNumber):
        return Board.alphabet[rowNumber] + " "

    def inner_board_end_row_marker(self, rowNumber):
        return " " + Board.alphabet[rowNumber] + "\n"


class Game:
    def __init__(self):
        self.reveal_callback = self.start_game
        self.errorQueue = []
        self.isInFlagMode = False

    def show_welcome_message(self):
        return (
            "Welcome to Minesweeper!\n"
            "What size minefield do you wish to play on?\n"
            "Say 1 for small, 2 for medium, and 3 for large.\n")

    def show_board(self):
        return (
            "Mines Left: " +
            str(self.mines - self.board.number_of_flags) + "\n"
            "\n" +
            str(self.board) +
            "\n" +
            self.show_prompt())

    def generate_board(self, width, height, mines):
        self.board = Board(width, height)
        self.mines = mines

    def toggle_flag_mode(self):
        self.isInFlagMode = not self.isInFlagMode

    def show_prompt(self):
        if self.check_end_game_loss():
            return "Ouch."
        elif self.check_end_game_win():
            return "Congrats, you've won!"
        elif self.isInFlagMode:
            return (
                "Enter an 'f' to exit flag mode\n"
                "Enter a coordinate to toggle the flag\n")
        else:
            return (
                "Enter an 'f' to enter flag mode\n"
                "Enter a coordinate to reveal a tile\n")

    def process_input(self, userInput):
        if len(userInput) == 3 and userInput[0].isalpha() and \
                userInput[2].isalpha() and userInput[1] == " ":
            x, y = self.alpha_to_coordinates(userInput[0], userInput[2])
            if self.isInFlagMode:
                self.board.toggle_flag(x, y)
            else:
                self.reveal(x, y)
        elif len(userInput) == 1 and userInput[0].lower() == 'f':
            self.toggle_flag_mode()
        else:
            self.errorQueue.append(
                "This isn't valid input. Try something like \"a a\"")

    def reveal(self, x, y):
        self.reveal_callback(x, y)

    def alpha_to_coordinates(self, a, b):
        x = self.board.alphabet.index(a.lower())
        y = self.board.alphabet.index(b.lower())
        return x, y

    def show_errors(self):
        for error in self.errorQueue:
            yield self.errorQueue.pop()

    def start_game(self, x, y):
        tile = self.board.convert_coordinate_to_tile(x, y)
        self.board.place_mines(self.mines, tile)
        self.board.reveal(x, y)
        self.reveal_callback = self.board.reveal

    def check_end_game_loss(self):
        return self.board.is_mine_triggered

    def check_end_game_win(self):
        for row in self.board.grid:
            for tile in row:
                if (tile.isHidden and not tile.isMine) \
                        or (tile.isMine and not tile.isFlagged):
                    return False

        return True
