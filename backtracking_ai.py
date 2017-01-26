from Minesweeper_tdd import Game, Board

class BacktrackingAI(object):
    class ModifiedBoard(Board):
        pass  # Just in case wrapper

    def __init__(self, game):
        self.game = game
        self.localBoard = BacktrackingAI.ModifiedBoard(game.board.width, game.board.height)

    def get_game_tile_from_local_board(self, localTile):
        return self.game.board.convert_coordinate_to_tile(*localTile.position)

    def update_local_board(self, revealedTiles):
        print "Revealed Tiles:", revealedTiles
        for tile in revealedTiles:
            localTile = self.localBoard.convert_coordinate_to_tile(*tile.position)
            localTile.nearbyMines = tile.nearbyMines
            localTile.reveal()
        print "After update:", self.localBoard.grid

    def first_tile(self):
        revealedTiles = self.game.reveal(self.localBoard.width // 2, self.localBoard.height // 2)
        self.update_local_board(revealedTiles)

    def next_move(self):
        self.flag_obvious_mines()
        print self.game.show_board()
        revealedTiles = self.reveal_obvious_tiles()
        if game.board.check_end_game_win():
            return
        if not revealedTiles:
            revealedTiles = self.backtracking_algorithm()
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
                    for s in unrevealedSurroundingTiles:
                        s.isFlagged = True
                        self.get_game_tile_from_local_board(s).isFlagged = True

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
                    # Check to see if there are hidden tiles around a number that already has the correct number of flagged tiles
                    if tile.nearbyMines == numFlagsAround and numHiddenTilesAround > numFlagsAround:
                        revealed = self.game.reveal(*tile.position)
                        print revealed
                        revealedTiles.extend(revealed)
                        print game.show_board()
        return revealedTiles

    def backtracking_algorithm(self):
        print "Had to backtrack"
        raw_input()
        return []


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
        print game.board.grid

    print game.show_board()
    ai = BacktrackingAI(game)
    ai.first_tile()

    while not game.board.check_end_game_win() and not game.board.check_end_game_loss():
        print game.show_board()
        ai.next_move()
    print game.show_board()
