# coding=utf-8
import random
from itertools import chain


class Board:
    alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u",
                "v", "w", "x", "y", "z", "aa", "bb", "cc", "dd"]

    class Tile:
        def __init__(self, x, y):
            self.position = (x, y)
            self.nearbyMines = 0
            self.isMine = False
            self.isHidden = True
            self.isFlagged = False

        def copy(self):
            new = Board.Tile(*self.position)
            new.nearbyMines = self.nearbyMines
            new.isMine = self.isMine
            new.isHidden = self.isHidden
            new.isFlagged = self.isFlagged
            return new

        def __repr__(self):
            return str(self.nearbyMines)

        def __str__(self):
            if not self.isHidden and self.isMine:
                if self.isFlagged:
                    return "⚐ "
                else:
                    return "X "

            if self.isFlagged:
                return "⚑ "
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

    def copy(self):
        new = Board(self.width, self.height)
        new.is_mine_triggered = self.is_mine_triggered
        new.number_of_flags = self.number_of_flags
        new.minePositions = self.minePositions[:]
        new.grid = []
        for row in self.grid:
            newRow = []
            for tile in row:
                newRow.append(tile.copy())
            new.grid.append(newRow)
        return new

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
            tile = self.convert_coordinate_to_tile(x, y)
            if tile.isHidden:
                if tile.toggle_flag():
                    self.number_of_flags += 1
                else:
                    self.number_of_flags -= 1

    def reveal(self, x, y):
        tilesRevealed = []
        if self.is_valid_coordinate(x, y):
            tile = self.convert_coordinate_to_tile(x, y)
            if not tile.isHidden and tile.nearbyMines > 0:
                numFlags = sum(map(lambda s: s.isFlagged, self.surrounding_tiles(tile)))
                if numFlags == tile.nearbyMines:
                    tilesRevealed = list(chain.from_iterable(
                        map(self.reveal_recursive, self.surrounding_tiles(tile)))) + self.reveal_recursive(tile)
            else:
                tilesRevealed = self.reveal_recursive(tile)
        self.check_end_game_win()
        return tilesRevealed

    def reveal_recursive(self, centerTile):
        if not centerTile.isFlagged:
            centerTile.reveal()
            tilesRevealed = [centerTile]
            if centerTile.isMine:
                self.is_mine_triggered = True
                self.reveal_whole_board()
            if centerTile.nearbyMines == 0:
                for tile in self.surrounding_tiles(centerTile):
                    if tile.isHidden and not tile.isFlagged:
                        tilesRevealed.extend(self.reveal_recursive(tile))
            return tilesRevealed
        else:
            return []

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

    def check_end_game_loss(self):
        return self.is_mine_triggered

    def check_end_game_win(self):
        for row in self.grid:
            for tile in row:
                if (tile.isHidden and not tile.isMine) \
                        or (tile.isMine and not tile.isFlagged):
                    return False
        self.reveal_whole_board()
        return True

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
            "\n")

    def generate_board(self, width, height, mines):
        self.board = Board(width, height)
        self.mines = mines

    def toggle_flag_mode(self):
        self.isInFlagMode = not self.isInFlagMode

    def show_prompt(self):
        if self.board.check_end_game_loss():
            return "Ouch."
        elif self.board.check_end_game_win():
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
        try:
            xAlpha, yAlpha = userInput.split()
            if xAlpha.lower() in self.board.alphabet and yAlpha in self.board.alphabet:
                x, y = self.alpha_to_coordinates(xAlpha, yAlpha)
                if self.isInFlagMode:
                    self.board.toggle_flag(x, y)
                else:
                    return self.reveal(x, y)
        except ValueError:
            if len(userInput) == 1 and userInput[0].lower() == 'f':
                self.toggle_flag_mode()
                return
            elif userInput == "show":
                return
        self.errorQueue.append(
            "This isn't valid input. Try something like \"a a\"")

    def reveal(self, x, y):
        return self.reveal_callback(x, y)

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
        revealed = self.board.reveal(x, y)
        self.reveal_callback = self.board.reveal
        return revealed


if __name__ == '__main__':
    game = Game()
    print game.show_welcome_message()
    size = int(input())
    if size == 1:
        game.generate_board(5, 5, 3)
    elif size == 2:
        game.generate_board(10, 5, 6)
    elif size == 3:
        game.generate_board(30, 16, 99)

    while not game.board.check_end_game_win() and not game.board.check_end_game_loss():
        print game.show_board()
        game.process_input(raw_input(game.show_prompt()))
    print game.show_board()
