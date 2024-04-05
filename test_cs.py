import unittest
import cairo
import char_surface as cs


class TestCharacterSurfaceCreation(unittest.TestCase):
    def setUp(self):
        # Setup tasks before each test method
        self.CHARACTER = "あ"
        self.FONT_SIZE = 72
        self.EDGE_LENGTH = 100

    def test_surface_size(self):
        surface = cs.create_blank(
            cairo.FORMAT_ARGB32, self.EDGE_LENGTH, self.EDGE_LENGTH
        )
        self.assertEqual(surface.get_width(), self.EDGE_LENGTH)
        self.assertEqual(surface.get_height(), self.EDGE_LENGTH)

    def test_background_is_white(self):
        surface = cs.create_blank(
            cairo.FORMAT_ARGB32, self.EDGE_LENGTH, self.EDGE_LENGTH
        )
        self.assertTrue(cs.is_pixel_white(surface, 0, 0))
        self.assertTrue(cs.is_pixel_white(surface, 1, 1))
        self.assertTrue(cs.is_pixel_white(surface, 0, 99))
        self.assertTrue(cs.is_pixel_white(surface, 99, 0))
        self.assertTrue(cs.is_pixel_white(surface, 99, 99))

    def test_colortesting_out_of_bounds(self):
        surface = cs.create_blank(
            cairo.FORMAT_ARGB32, self.EDGE_LENGTH, self.EDGE_LENGTH
        )
        with self.assertRaises(ValueError):
            self.assertRaises(cs.is_pixel_white(surface, 100, 100))
        with self.assertRaises(ValueError):
            self.assertRaises(cs.is_pixel_white(surface, 100, 0))
        with self.assertRaises(ValueError):
            self.assertRaises(cs.is_pixel_white(surface, 0, 100))

    def test_draw_horizontal_rules(self):
        surface = cs.create_blank(
            cairo.FORMAT_ARGB32, self.EDGE_LENGTH, self.EDGE_LENGTH
        )
        new_surface = cs.draw_horizontal_rule(surface)

        for y in [20, 80]:
            # dash on
            self.assertFalse(cs.is_pixel_white(new_surface, 0, y))
            self.assertFalse(cs.is_pixel_white(new_surface, 1, y))
            # dash off
            self.assertTrue(cs.is_pixel_white(new_surface, 2, y))
            self.assertTrue(cs.is_pixel_white(new_surface, 3, y))
            self.assertTrue(cs.is_pixel_white(new_surface, 4, y))
            self.assertTrue(cs.is_pixel_white(new_surface, 5, y))
            # dash on
            self.assertFalse(cs.is_pixel_white(new_surface, 6, y))
            self.assertFalse(cs.is_pixel_white(new_surface, 7, y))
            # dash off
            self.assertTrue(cs.is_pixel_white(new_surface, 8, y))
            self.assertTrue(cs.is_pixel_white(new_surface, 9, y))
            self.assertTrue(cs.is_pixel_white(new_surface, 10, y))

    def test_bounding_box(self):
        surface = cs.create_blank(
            cairo.FORMAT_ARGB32, self.EDGE_LENGTH, self.EDGE_LENGTH
        )
        new_surface = cs.draw_bounding_box(surface)

        # Test horizontal lines at y=10 and y=90
        for y in [10, 90]:
            for x in range(0, self.EDGE_LENGTH):
                # Expect non-white (line) pixels across the entire row
                self.assertFalse(cs.is_pixel_white(new_surface, x, y))

        # Test vertical lines at x=0 and x=99
        for x in [0, 99]:
            for y in range(10, 91):  # From row 10 to row 90 inclusive
                # Expect non-white (line) pixels down the entire column
                self.assertFalse(cs.is_pixel_white(new_surface, x, y))

    def test_draw_character(self):
        new_surface = cs.draw_character("は")

        # spot check surface is white
        self.assertTrue(cs.is_pixel_white(new_surface, 0, 0))
        self.assertTrue(cs.is_pixel_white(new_surface, 1, 0))
        # spot check certain points are non-white where char is drawn
        self.assertFalse(cs.is_pixel_white(new_surface, 25, 35))
        self.assertFalse(cs.is_pixel_white(new_surface, 60, 40))

    def test_stack_surfaces(self):
        stacking_surface = cs.draw_character("は")

        surface = cs.create_blank(
            cairo.FORMAT_ARGB32, self.EDGE_LENGTH, self.EDGE_LENGTH
        )

        new_surface = cs.stack_surfaces(surface, stacking_surface)

        # spot check surface is white
        self.assertTrue(cs.is_pixel_white(new_surface, 0, 0))
        self.assertTrue(cs.is_pixel_white(new_surface, 1, 0))
        # spot check certain points are non-white where char is drawn
        self.assertFalse(cs.is_pixel_white(new_surface, 25, 35))
        self.assertFalse(cs.is_pixel_white(new_surface, 60, 40))


if __name__ == "__main__":
    unittest.main()
