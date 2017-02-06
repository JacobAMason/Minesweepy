import time

from Minesweeper_tdd import Game, Board


class BacktrackingAI(object):
    def __init__(self, game):
        self.game = game
        self.localBoard = Board(game.board.width, game.board.height)
        # Override Tiles to have isMine be None so it can be used as a ternary field for determining
        # whether or not a space has been decided as a mine during the recursive backtracking stage
        for row in self.localBoard.grid:
            for tile in row:
                tile.isMine = None

    def first_tile(self):
        revealedTiles = self.game.reveal(self.localBoard.width // 2, self.localBoard.height // 2)
        self.update_local_board(revealedTiles)

    def next_move(self):
        self.flag_obvious_mines()
        print self.game.show_board()
        revealedTiles = self.reveal_obvious_tiles()
        print self.game.show_board()
        if game.board.check_end_game_win():
            return
        if not revealedTiles:
            revealedTiles = self.backtracking_algorithm()
            if not revealedTiles:
                # If we end up here, there was no tile that is consistent across all solutions
                print self.game.show_board()
                revealedTiles = self.game.process_input(raw_input(
                    game.show_prompt() + "\nThe AI has to guess\n"))
        if revealedTiles is not None:
            self.update_local_board(revealedTiles)

    def flag_obvious_mines(self):
        print "Flagging obvious mines"
        for row in self.localBoard.grid:
            for tile in row:
                if tile.isHidden or tile.nearbyMines == 0:
                    continue
                surroundingTiles = self.localBoard.surrounding_tiles(tile)
                unrevealedSurroundingTiles = filter(lambda s: s.isHidden, surroundingTiles)
                if len(unrevealedSurroundingTiles) == tile.nearbyMines:
                    for s in filter(lambda s: not s.isFlagged, unrevealedSurroundingTiles):
                        print "Marked", s.position, "as a mine"
                        s.toggle_flag()
                        s.set_as_mine()
                        self.game.board.toggle_flag(*s.position)

    def reveal_obvious_tiles(self):
        print "Revealing obvious tiles"
        revealedTiles = []
        for row in self.localBoard.grid:
            for tile in row:
                if not tile.isHidden and tile.nearbyMines > 0:
                    numFlagsAround = 0
                    numHiddenTilesAround = 0
                    for s in self.localBoard.surrounding_tiles(tile):
                        if s.isFlagged:
                            numFlagsAround += 1
                        if s.isHidden:
                            numHiddenTilesAround += 1  # Flagged tiles are also hidden tiles
                    # Check to see if there are hidden tiles around a number
                    # that already has the correct number of flagged tiles
                    if tile.nearbyMines == numFlagsAround and numHiddenTilesAround > numFlagsAround:
                        revealed = self.game.reveal(*tile.position)
                        revealedTiles.extend(revealed)
        return revealedTiles

    def backtracking_algorithm(self):
        BF_LIMIT = 8
        print "Had to backtrack"
        raw_input()
        startTime = time.time()

        borderTiles = []
        allEmptyTiles = []

        for row in self.localBoard.grid:
            for tile in row:
                if not tile.isFlagged:
                    if tile.isHidden:
                        allEmptyTiles.append(tile)
                    if self.isBoundary(tile):
                        borderTiles.append(tile)

        numberOfUnknowableTiles = len(allEmptyTiles) - len(borderTiles)
        borderOptimization = numberOfUnknowableTiles > BF_LIMIT
        if not borderOptimization:
            borderTiles = allEmptyTiles

        print "borderOptimization", borderOptimization

        if not len(borderTiles):
            raise ValueError("Backtracking has no tiles to examine. Something went wrong.")

        if borderOptimization:
            borderSegments = self.segregate_border_tiles(borderTiles)
        else:
            borderSegments = [borderTiles]

        revealedTiles = []
        print "There are", len(borderSegments), "segments"
        raw_input()
        for i, segment in enumerate(borderSegments):
            print "START BACKTRACKING ON SEGMENT", i + 1
            segment = list(map(lambda tile: tile.position, segment))
            solutions = []
            self.backtrack_recursive(segment, self.localBoard.copy(), solutions, depth=0)
            # solutions is pass-by-reference thanks to how Python's lists work

            if not len(solutions):
                raise ValueError("Backtracking couldn't find a solution. Something went wrong.")

            for tilePosition in segment:
                if self.is_tile_consistent(tilePosition, solutions):
                    print tilePosition, "is consistent throughout all solutions"
                    if solutions[0].convert_coordinate_to_tile(*tilePosition).isFlagged:
                        self.localBoard.convert_coordinate_to_tile(*tilePosition).isMine = True
                        self.localBoard.toggle_flag(*tilePosition)
                        self.game.board.toggle_flag(*tilePosition)
                    else:
                        revealedTiles.extend(self.game.board.reveal(*tilePosition))

        print "finished backtracking in", time.time() - startTime, "seconds"
        print "revealed", list(map(lambda tile: tile.position, revealedTiles))
        return revealedTiles

    def is_tile_consistent(self, tilePosition, solutions):
        return all(solutions[0].convert_coordinate_to_tile(*tilePosition).isFlagged == sln for sln in
                   map(lambda solution: solution.convert_coordinate_to_tile(*tilePosition).isFlagged, solutions[1:]))

    def isBoundary(self, tile):
        # A boundary tile is a hidden tile with revealed tiles near it.
        if not tile.isHidden:
            return False
        else:
            return any(map(lambda s: not s.isHidden, self.localBoard.surrounding_tiles(tile)))

    def segregate_border_tiles(self, borderTiles):
        allRegions = []  # List of list of tiles
        covered = []  # List of tiles

        while True:
            queue = []  # Queue of tiles
            region = []  # List of tiles

            # Find a suitable starting point
            for tile in borderTiles:
                if tile not in covered:
                    region.append(tile)
                    covered.append(tile)
                    queue.append(tile)
                    break

            if not queue:
                break

            while queue:
                currentTile = queue.pop(0)

                for tile in self.localBoard.surrounding_tiles(currentTile):
                    if tile in borderTiles and tile not in region:
                        region.append(tile)
                        covered.append(tile)
                        queue.append(tile)
                    elif tile.nearbyMines > 0:
                        for s in filter(lambda s: s in borderTiles and s not in queue and s not in region,
                                        self.localBoard.surrounding_tiles(tile)):
                            queue.append(s)

            allRegions.append(region)

        return allRegions

    def backtrack_recursive(self, segment, board, solutions, depth):
        # If the board is not consistent, return. This is the backtrack
        if not self.is_board_consistent(board):
            return

        # If we've recursed the same number of times as their are tiles,
        # we've found a solution.
        if depth == len(segment):
            # if board.number_of_flags < self.game.mines:  #TODO: and not borderOptimizaton
            #     return
            print "Found solution"
            print board
            solutions.append(board)
            return

        # Recursive step
        markedAsMine = board.copy()
        markedAsMine.toggle_flag(*segment[depth])
        markedAsMine.convert_coordinate_to_tile(*segment[depth]).set_as_mine()
        self.backtrack_recursive(segment, markedAsMine, solutions, depth=depth + 1)  # With mine
        markedAsNotAMine = board.copy()
        markedAsNotAMine.convert_coordinate_to_tile(*segment[depth]).isMine = False
        self.backtrack_recursive(segment, markedAsNotAMine, solutions, depth=depth + 1)  # Without mine

    def is_board_consistent(self, board):
        for row in board.grid:
            for tile in row:
                if tile.isHidden:
                    continue
                surroundingTiles = list(board.surrounding_tiles(tile))

                numberOfFlagsAroundTile = sum((s.isMine is True for s in surroundingTiles))
                if numberOfFlagsAroundTile > tile.nearbyMines:
                    return False

                numberOfFreeSpaces = sum((s.isHidden and s.isMine is None for s in surroundingTiles))
                if numberOfFreeSpaces < tile.nearbyMines - numberOfFlagsAroundTile:
                    return False
        return board.number_of_flags <= self.game.mines

    def update_local_board(self, revealedTiles):
        for tile in revealedTiles:
            localTile = self.localBoard.convert_coordinate_to_tile(*tile.position)
            localTile.nearbyMines = tile.nearbyMines
            localTile.reveal()
        self.localBoard.number_of_flags = self.game.board.number_of_flags


if __name__ == '__main__':
    game = Game()
    print game.show_welcome_message()
    size = int(input())
    if size == 1:
        game.generate_board(8, 8, 10)
    elif size == 2:
        game.generate_board(16, 16, 40)
    elif size == 3:
        game.generate_board(30, 16, 99)
    elif size == 4:
        game.generate_board(8, 8, 1)
    elif size == 5:
        game.board = Board(8, 8)
        game.mines = 10
        for coords in [(7, 1), (2, 2), (0, 3), (2, 6), (3, 6), (6, 6), (1, 7), (3, 7), (4, 7), (6, 7)]:
            tile = game.board.convert_coordinate_to_tile(*coords)
            tile.set_as_mine()
            game.board.increment_tiles_around_mine(tile)
            game.board.minePositions.append(tile)
        game.reveal_callback = game.board.reveal
    elif size == 6:
        game.board = Board(6, 6)
        game.mines = 8
        for coords in [(2, 0), (3, 0), (0, 2), (0, 3), (5, 2), (5, 3), (2, 5), (3, 5)]:
            tile = game.board.convert_coordinate_to_tile(*coords)
            tile.set_as_mine()
            game.board.increment_tiles_around_mine(tile)
            game.board.minePositions.append(tile)
        game.reveal_callback = game.board.reveal
    elif size == 7:
        game.board = Board(30, 16)
        game.mines = 99
        for coords in [(0, 0), (2, 0), (5, 0), (3, 1), (5, 1), (18, 1), (22, 1), (24, 1), (26, 1), (4, 2), (5, 2),
                       (10, 2), (17, 2), (18, 2), (19, 2), (21, 2), (26, 2), (1, 3), (2, 3), (4, 3), (7, 3), (18, 3),
                       (22, 3), (24, 3), (25, 3), (26, 3), (4, 4), (7, 4), (13, 4), (16, 4), (22, 4), (3, 5), (5, 5),
                       (6, 5), (10, 5), (12, 5), (17, 5), (20, 5), (23, 5), (3, 6), (18, 6), (19, 6), (20, 6), (0, 7),
                       (4, 7), (7, 7), (8, 7), (12, 7), (21, 7), (23, 7), (24, 7), (0, 8), (2, 8), (6, 8), (9, 8),
                       (12, 8), (26, 8), (29, 8), (2, 9), (4, 9), (6, 9), (8, 9), (20, 9), (24, 9), (28, 9), (2, 10),
                       (8, 10), (20, 10), (29, 10), (0, 11), (1, 11), (6, 11), (9, 11), (10, 11), (12, 11), (19, 11),
                       (22, 11), (3, 12), (6, 12), (8, 12), (20, 12), (27, 12), (29, 12), (0, 13), (9, 13), (10, 13),
                       (11, 13), (13, 13), (16, 13), (24, 13), (5, 14), (15, 14), (17, 14), (22, 14), (24, 14),
                       (13, 15), (19, 15), (23, 15), (28, 15)]:
            tile = game.board.convert_coordinate_to_tile(*coords)
            tile.set_as_mine()
            game.board.increment_tiles_around_mine(tile)
            game.board.minePositions.append(tile)
        game.reveal_callback = game.board.reveal

    print game.show_board()
    ai = BacktrackingAI(game)
    ai.first_tile()
    game.show_board()

    while not game.board.check_end_game_win() and not game.board.check_end_game_loss():
        ai.next_move()
    print game.show_board()

    minePositions = []
    for row in game.board.grid:
        for tile in row:
            if tile.isFlagged:
                minePositions.append(tile.position)
    print minePositions
