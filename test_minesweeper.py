# coding=utf-8
import unittest
from Minesweeper_tdd import Game, Board

__author__ = 'JacobAMason'


class TileTests(unittest.TestCase):
    def setUp(self):
        self.tile = Board.Tile(0, 0)

    def test_default_values(self):
        self.assertEqual(self.tile.position, (0, 0))
        self.assertEqual(self.tile.nearbyMines, 0)
        self.assertEqual(self.tile.isMine, False)
        self.assertEqual(self.tile.isHidden, True)
        self.assertEqual(self.tile.isFlagged, False)

    def test_reveal_tile(self):
        self.tile.reveal()
        self.assertFalse(self.tile.isHidden)

    def test_flag_tile(self):
        self.tile.toggle_flag()
        self.assertTrue(self.tile.isHidden)

    def test_unflag_tile(self):
        self.tile.toggle_flag()
        self.tile.toggle_flag()
        self.assertTrue(self.tile.isHidden)

    def test_set_number(self):
        self.tile.set_number_of_nearby_mines(4)
        self.assertEqual(self.tile.nearbyMines, 4)

    def test_set_mine(self):
        self.tile.set_as_mine()
        self.assertTrue(self.tile.isMine)


class Board2x3Tests(unittest.TestCase):
    def setUp(self):
        self.board = Board(width=2, height=3)
        self.tile = self.board.grid[1][0]

    def test_initialize_blank_board(self):
        visibilityGrid = [[tile.isHidden for tile in row] for row in
                          self.board.grid]

        self.assertEqual(
            visibilityGrid,
            [[True, True],
             [True, True],
             [True, True]]
        )

    def test_show_blank_board(self):
        self.assertEqual(
            str(self.board),
            (
                "  a b\n"
                "a ████ a\n"
                "b ████ b\n"
                "c ████ c\n"
                "  a b\n")
        )

    def test_initialize_0_mines(self):
        mineGrid = [[tile.isMine for tile in row] for row in self.board.grid]

        self.assertEqual(
            mineGrid,
            [[False, False],
             [False, False],
             [False, False]]
        )

    def test_initialize_1_mine(self):
        self.board.place_mines(1, self.tile)
        mineGrid = [[tile.isMine for tile in row] for row in self.board.grid]

        self.assertTrue(
            any([any(mineGrid[0]),
                 any(mineGrid[1]),
                 any(mineGrid[2])])
        )

    def test_initialize_full_mines(self):
        self.board.place_mines(5, self.tile)
        mineGrid = [[tile.isMine for tile in row] for row in self.board.grid]

        self.assertEqual(
            mineGrid,
            [[True, True],
             [False, True],
             [True, True]]
        )

    def test_number_of_nearby_mines_update_when_mine_is_added(self):
        self.tile.set_as_mine()
        self.board.increment_tiles_around_mine(self.tile)

        numberGrid = [[tile.nearbyMines for tile in row] for row in
                      self.board.grid]

        self.assertEqual(
            numberGrid,
            [[1, 1],
             [0, 1],
             [1, 1]]
        )

    def test_reveal(self):
        self.board.reveal(0, 1)
        visibilityGrid = [[tile.isHidden for tile in row] for row in
                          self.board.grid]

        self.assertEqual(
            visibilityGrid,
            [[False, False],
             [False, False],
             [False, False]]
        )

    def test_reveal_print(self):
        self.board.reveal(0, 1)

        self.assertEqual(
            str(self.board),
            (
                "  a b\n"
                "a      a\n"
                "b      b\n"
                "c      c\n"
                "  a b\n")
        )

    def test_cannot_recursively_reveal_tile_near_mine(self):
        self.tile.set_as_mine()
        self.board.increment_tiles_around_mine(self.tile)
        self.board.reveal(1, 1)
        visibilityGrid = [[tile.isHidden for tile in row] for row in
                          self.board.grid]

        self.assertEqual(
            visibilityGrid,
            [[True, True],
             [True, False],
             [True, True]]
        )

    def test_cannot_recursively_reveal_tile_near_mine_print(self):
        self.tile.set_as_mine()
        self.board.increment_tiles_around_mine(self.tile)
        self.board.reveal(1, 1)

        self.assertEqual(
            str(self.board),
            (
                "  a b\n"
                "a ████ a\n"
                "b ██1  b\n"
                "c ████ c\n"
                "  a b\n")
        )

    def test_flag_tile(self):
        self.board.toggle_flag(0, 1)
        flaggedGrid = [[tile.isFlagged for tile in row] for row in
                       self.board.grid]

        self.assertEqual(
            flaggedGrid,
            [[False, False],
             [True, False],
             [False, False]]
        )

    def test_flag_tile_print(self):
        self.board.toggle_flag(0, 1)

        self.assertEqual(
            str(self.board),
            (
                "  a b\n"
                "a ████ a\n"
                "b ▓▓██ b\n"
                "c ████ c\n"
                "  a b\n")
        )

    def test_cannot_reveal_flagged_tile(self):
        self.board.toggle_flag(0, 1)
        self.board.reveal(0, 1)
        visibilityGrid = [[tile.isHidden for tile in row] for row in
                          self.board.grid]

        self.assertEqual(
            visibilityGrid,
            [[True, True],
             [True, True],
             [True, True]]
        )

    def test_cannot_recursively_reveal_flagged_tile(self):
        self.board.toggle_flag(0, 1)
        self.board.reveal(1, 1)
        visibilityGrid = [[tile.isHidden for tile in row] for row in
                          self.board.grid]

        self.assertEqual(
            visibilityGrid,
            [[False, False],
             [True, False],
             [False, False]]
        )

    def test_mine_triggered(self):
        self.board.grid[1][0].set_as_mine()
        self.board.reveal(0, 1)

        self.assertTrue(self.board.is_mine_triggered)


class GameTests(unittest.TestCase):
    def setUp(self):
        self.game = Game(2, 3, mines=1)

    def test_show_welcome_message(self):
        self.assertEqual(
            self.game.show_welcome_message(), "Welcome to Minesweeper!"
        )

    def test_create_empty_board(self):
        self.assertEqual(self.game.mines, 1)

    def test_show_board(self):
        self.assertEqual(
            self.game.show_board(),
            (
                "Mines Left: 1\n"
                "\n"
                "  a b\n"
                "a ████ a\n"
                "b ████ b\n"
                "c ████ c\n"
                "  a b\n"
                "\n"
                "Enter an 'f' to enter flag mode\n"
                "Enter a coordinate to reveal a tile\n")
        )

    def test_reveal_tile_on_empty_board(self):
        self.game.process_input("a b")
        visibilityGrid = [[tile.isHidden for tile in row] for row in
                          self.game.board.grid]

        self.assertEqual(
            visibilityGrid,
            [[False, False],
             [False, False],
             [False, False]]
        )

    def test_toggle_flag_mode(self):
        self.game.toggle_flag_mode()
        self.assertEqual(
            self.game.show_prompt(),
            (
                "Enter an 'f' to exit flag mode\n"
                "Enter a coordinate to toggle the flag\n")
        )

    def test_toggle_flag(self):
        self.game.toggle_flag_mode()
        self.game.process_input("a b")
        flaggedGrid = [[tile.isFlagged for tile in row] for row in
                       self.game.board.grid]

        self.assertEqual(
            flaggedGrid,
            [[False, False],
             [True, False],
             [False, False]]
        )

    def test_user_enter_flag_mode(self):
        self.game.process_input("f")
        self.assertTrue(self.game.isInFlagMode)

    def test_error_queue(self):
        self.game.process_input("FOO BAR")

        self.assertEqual(
            list(self.game.show_errors())[0],
            "This isn't valid input. Try something like \"a a\""
        )

    def test_start_game(self):
        self.game.start_game(0, 1)
        visibilityGrid = [[tile.isHidden for tile in row] for row in
                          self.game.board.grid]

        self.assertEqual(
            visibilityGrid,
            [[True, True],
             [False, True],
             [True, True]]
        )

    def test_check_end_game(self):
        self.game.board = Board(2, 3)
        self.game.board.place_mines(5, self.game.board.grid[1][0])
        self.game.board.reveal(0, 0)

        self.assertTrue(self.game.check_end_game())


if __name__ == '__main__':
    unittest.main()
