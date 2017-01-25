#!python3
import random
import os


class Board:
    from enum import IntEnum, unique

    # Used to handle tile states
    @unique
    class _tile(IntEnum):
        revealed = -4
        hidden = -3
        flagged = -2
        mine = -1
        blank = 0

    _alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
                 "u", "v", "w", "x", "y", "z"]

    def __init__(self, sizeX, sizeY, mines, startX, startY, randSeed=None):
        # translate input size into board sizes. (Obviously, you can change this and create custom board sizes.)
        if sizeX > 0 and sizeX <= 26 and sizeY > 0 and sizeY <= 26:
            self.sizeX = int(sizeX)
            self.sizeY = int(sizeY)
        else:
            raise ValueError("Invalid board size. Must be between 1 and 26")

        if mines > 0 and mines < (self.sizeX * self.sizeY) / 2:
            self.mines = int(mines)
        else:
            raise ValueError("Invalid number of mines.")

        # Make sure that the starting coordinate given is valid for this board size.
        if startX not in range(self.sizeX) or startY not in range(self.sizeY):
            raise IndexError("Invalid starting coordinate for this board size.")

        # Construct blank boards. Grid contains the value of a cell and visibility contains the state of a cell (hidden, revealed, or flagged)
        self.grid = [[Board._tile.blank for j in range(self.sizeX)] for i in range(self.sizeY)]
        self.visibility = [[Board._tile.hidden for j in range(self.sizeX)] for i in range(self.sizeY)]
        self.minePositions = []
        self.flags = 0

        # If a seed is provided, use it.
        if randSeed is not None:
            random.seed(randSeed)

        # calculate mine posotions
        for i in range(self.mines):
            xmine = random.randint(0, self.sizeX - 1)
            ymine = random.randint(0, self.sizeY - 1)
            while (xmine, ymine) in self.minePositions or (xmine, ymine) == (startX, startY):
                xmine = random.randint(0, self.sizeX - 1)
                ymine = random.randint(0, self.sizeY - 1)
            self.grid[ymine][xmine] = 9
            self.minePositions.append((xmine, ymine))
            for x, y in self._getSurroundingCoordList(xmine, ymine):
                self.grid[y][x] += 1

        # place mines on the board.
        for x, y in self.minePositions:
            self.grid[y][x] = Board._tile.mine

        self._reveal(startX, startY)

    # print board
    def __repr__(self):
        rtnString = "  " + " ".join(Board._alphabet[:self.sizeX]) + "\n"
        for j, row in enumerate(self.visibility):
            rtnString += Board._alphabet[j] + " "
            for i, e in enumerate(row):
                if e is Board._tile.revealed:
                    rtnString += (" " if self.grid[j][i] is Board._tile.blank else (
                    "*" if self.grid[j][i] is Board._tile.mine else str(self.grid[j][i]))) + " "
                elif e is Board._tile.flagged:
                    rtnString += "▓▓"
                else:
                    rtnString += "██"
            rtnString += Board._alphabet[j] + "\n"
        rtnString += "  " + " ".join(Board._alphabet[:self.sizeX]) + "\n"
        return rtnString

    # Generator which yields the coordinates of any surrounding cells
    def _getSurroundingCoordList(self, x, y):
        surroundingPositions = [(x - 1, y - 1), (x, y - 1), (x + 1, y - 1), (x - 1, y), (x + 1, y), (x - 1, y + 1),
                                (x, y + 1), (x + 1, y + 1)]
        for x, y in surroundingPositions:
            if x in range(self.sizeX) and y in range(self.sizeY):
                yield x, y

    # Converts alphabetical entries into numeric coordinates.
    def _alphaToCoords(self, a, b):
        if a not in Board._alphabet or b not in Board._alphabet:
            print("These aren't letters. Try something like \"a a\"")
            return -1, -1

        x = Board._alphabet.index(a)
        y = Board._alphabet.index(b)

        if x not in range(self.sizeX) or y not in range(self.sizeY):
            print("These coordinates won't do, they aren't on the board.")
            return -1, -1

        return x, y

    # Recursively unhide cells.
    def _reveal(self, x, y):
        self.visibility[y][x] = Board._tile.revealed

        if self.grid[y][x] is Board._tile.mine:
            return False
        elif self.grid[y][x] is Board._tile.blank:
            for i, j in self._getSurroundingCoordList(x, y):
                if self.visibility[j][i] is Board._tile.hidden:
                    self._reveal(i, j)

        return True

    # This remove fires once whenever a user instructs a cell to be revealed.
    def reveal(self, a, b):
        x, y = self._alphaToCoords(a, b)

        if (x, y) == (-1, -1):
            return True

        if self.visibility[y][x] is Board._tile.flagged:
            print("This space is flagged. You must unflag this position before checking here.")
            return True
        elif self.visibility[y][x] is Board._tile.revealed and self.grid[y][x] is not Board._tile.blank:
            flags = 0
            for i, j in self._getSurroundingCoordList(x, y):
                if self.visibility[j][i] is Board._tile.flagged:
                    flags += 1
            if flags == self.grid[y][x]:
                return all([self._reveal(i, j) if self.visibility[j][i] is Board._tile.hidden else True for i, j in
                            self._getSurroundingCoordList(x, y)])

        return self._reveal(x, y)

        # Add or remove a flag

    def toggleFlag(self, a, b):
        x, y = self._alphaToCoords(a, b)

        if (x, y) == (-1, -1):
            return

        if self.visibility[y][x] is Board._tile.flagged:
            self.visibility[y][x] = Board._tile.hidden
            self.flags -= 1
        elif self.visibility[y][x] is Board._tile.hidden:
            self.visibility[y][x] = Board._tile.flagged
            self.flags += 1
        else:
            print("You cannot flag this space.")

    # Returns true if there are still hidden cells, otherwise, it returns false.
    def _checkEndGame(self):
        for row in self.visibility:
            if Board._tile.hidden in row:
                return True

        return (self.mines != self.flags)

    # The running loop thar prompts users for input.
    def run(self):
        prompt = ""
        while self._checkEndGame():
            print("Mines Left:", self.mines - self.flags)
            print()
            print(self)
            print()
            print("Type 'f' to toggle flag mode, otherwise, enter a space to reveal.")
            readIn = input(prompt)
            os.system("cls")
            if readIn == "f":
                if prompt == "":
                    prompt = "f> "
                else:
                    prompt = ""
                continue
            elif len(readIn) == 3 and readIn[0] in Board._alphabet and readIn[2] in Board._alphabet and readIn[
                1] == " ":
                if prompt == "":
                    if not self.reveal(readIn[0], readIn[2]):
                        break
                else:
                    self.toggleFlag(readIn[0], readIn[2])

        # handle end-game
        if not self._checkEndGame():
            print("Mines Left:", self.mines - self.flags)
            print()
            print(self)
            print()
            print("A winner is you!")
        else:
            for j, row in enumerate(self.visibility):
                for i, e in enumerate(row):
                    if e is Board._tile.hidden:
                        self.visibility[j][i] = Board._tile.revealed

            print("Mines Left:", self.mines - self.flags)
            print()
            print(self)
            print()
            print("Whoops, you lose.")


if __name__ == '__main__':
    B = Board(sizeX=3, sizeY=3, mines=3, startX=0, startY=0)
    B.run()
