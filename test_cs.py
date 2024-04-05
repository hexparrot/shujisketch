import unittest
import cairo
import char_surface as cs


class TestCharacterSurfaceCreation(unittest.TestCase):
    def setUp(self):
        pass

    def test_surface_size(self):
        surface = cs.create_blank(cairo.FORMAT_ARGB32, cs.TILE_WIDTH, cs.TILE_HEIGHT)
        self.assertEqual(surface.get_width(), cs.TILE_HEIGHT)
        self.assertEqual(surface.get_height(), cs.TILE_WIDTH)

    def test_background_is_white(self):
        surface = cs.create_blank(cairo.FORMAT_ARGB32, cs.TILE_WIDTH, cs.TILE_HEIGHT)
        self.assertTrue(cs.is_pixel_white(surface, 0, 0))
        self.assertTrue(cs.is_pixel_white(surface, 1, 1))
        self.assertTrue(cs.is_pixel_white(surface, 0, 99))
        self.assertTrue(cs.is_pixel_white(surface, 99, 0))
        self.assertTrue(cs.is_pixel_white(surface, 99, 99))

    def test_colortesting_out_of_bounds(self):
        surface = cs.create_blank(cairo.FORMAT_ARGB32, cs.TILE_WIDTH, cs.TILE_HEIGHT)
        with self.assertRaises(ValueError):
            self.assertRaises(cs.is_pixel_white(surface, 100, 100))
        with self.assertRaises(ValueError):
            self.assertRaises(cs.is_pixel_white(surface, 100, 0))
        with self.assertRaises(ValueError):
            self.assertRaises(cs.is_pixel_white(surface, 0, 100))

    def test_apply_horizontal_rules(self):
        surface = cs.create_blank(cairo.FORMAT_ARGB32, cs.TILE_WIDTH, cs.TILE_HEIGHT)
        new_surface = cs.apply_horizontal_rule(surface)

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
        surface = cs.create_blank(cairo.FORMAT_ARGB32, cs.TILE_WIDTH, cs.TILE_HEIGHT)
        new_surface = cs.apply_bounding_box(surface)

        # Test horizontal lines at y=10 and y=90
        for y in [10, 90]:
            for x in range(0, cs.TILE_WIDTH):
                # Expect non-white (line) pixels across the entire row
                self.assertFalse(cs.is_pixel_white(new_surface, x, y))

        # Test vertical lines at x=0 and x=99
        for x in [0, 99]:
            for y in range(10, 91):  # From row 10 to row 90 inclusive
                # Expect non-white (line) pixels down the entire column
                self.assertFalse(cs.is_pixel_white(new_surface, x, y))

    def test_draw_character(self):
        new_surface = cs.draw_character("は")

        # spot check surface is transparent
        self.assertFalse(cs.is_pixel_white(new_surface, 0, 0))
        self.assertFalse(cs.is_pixel_white(new_surface, 1, 0))
        # spot check certain points are non-white where char is drawn
        self.assertFalse(cs.is_pixel_white(new_surface, 25, 35))
        self.assertFalse(cs.is_pixel_white(new_surface, 60, 40))

    def test_stack_surfaces(self):
        stacking_surface = cs.draw_character("は")

        surface = cs.create_blank(cairo.FORMAT_ARGB32, cs.TILE_WIDTH, cs.TILE_HEIGHT)

        new_surface = cs.stack_surfaces(surface, stacking_surface)

        # spot check surface is white
        self.assertTrue(cs.is_pixel_white(new_surface, 0, 0))
        self.assertTrue(cs.is_pixel_white(new_surface, 1, 0))
        # spot check certain points are non-white where char is drawn
        self.assertFalse(cs.is_pixel_white(new_surface, 25, 35))
        self.assertFalse(cs.is_pixel_white(new_surface, 60, 40))

    def test_stack_surfaces_x_offset(self):
        stacking_surface = cs.draw_character("は")

        surface = cs.create_blank(
            cairo.FORMAT_ARGB32, cs.TILE_WIDTH * 2, cs.TILE_HEIGHT
        )  # twice as wide

        new_surface = cs.stack_surfaces(surface, stacking_surface, x_offset=100)

        # spot check surface is white
        self.assertTrue(cs.is_pixel_white(new_surface, 0, 0))
        self.assertTrue(cs.is_pixel_white(new_surface, 1, 0))
        self.assertTrue(cs.is_pixel_white(new_surface, 25, 35))
        self.assertTrue(cs.is_pixel_white(new_surface, 60, 40))

        # spot check certain points are non-white where char is drawn
        self.assertFalse(cs.is_pixel_white(new_surface, 125, 35))
        self.assertFalse(cs.is_pixel_white(new_surface, 160, 40))

    def test_stack_surfaces_y_offset(self):
        stacking_surface = cs.draw_character("は")

        surface = cs.create_blank(
            cairo.FORMAT_ARGB32, cs.TILE_WIDTH, cs.TILE_HEIGHT * 2
        )  # twice as tall

        new_surface = cs.stack_surfaces(surface, stacking_surface, y_offset=100)

        # spot check surface is white
        self.assertTrue(cs.is_pixel_white(new_surface, 0, 0))
        self.assertTrue(cs.is_pixel_white(new_surface, 1, 0))
        self.assertTrue(cs.is_pixel_white(new_surface, 25, 35))
        self.assertTrue(cs.is_pixel_white(new_surface, 60, 40))

        # spot check certain points are non-white where char is drawn
        self.assertFalse(cs.is_pixel_white(new_surface, 25, 135))
        self.assertFalse(cs.is_pixel_white(new_surface, 60, 140))

    def test_full_character(self):
        stacking_surface = cs.draw_character("は")

        surface = cs.create_blank(cairo.FORMAT_ARGB32, cs.TILE_WIDTH, cs.TILE_HEIGHT)

        ruled_surface = cs.apply_horizontal_rule(surface)
        boxed_surface = cs.apply_bounding_box(ruled_surface)
        boxed_surface = cs.apply_bounding_box(boxed_surface, 100, 0)

        new_surface = cs.stack_surfaces(boxed_surface, stacking_surface)

        # spot check surface is white
        self.assertTrue(cs.is_pixel_white(new_surface, 0, 0))
        self.assertTrue(cs.is_pixel_white(new_surface, 1, 0))
        # spot check certain points are non-white where char is drawn
        self.assertFalse(cs.is_pixel_white(new_surface, 25, 35))
        self.assertFalse(cs.is_pixel_white(new_surface, 60, 40))

        for y in [20, 80]:
            # dash on
            self.assertFalse(cs.is_pixel_white(new_surface, 0, y))
            self.assertFalse(cs.is_pixel_white(new_surface, 1, y))
            # dash off
            self.assertTrue(cs.is_pixel_white(new_surface, 2, y))
            self.assertTrue(cs.is_pixel_white(new_surface, 3, y))
            self.assertTrue(cs.is_pixel_white(new_surface, 4, y))
            self.assertTrue(cs.is_pixel_white(new_surface, 5, y))

        # Test horizontal lines at y=10 and y=90
        for y in [10, 90]:
            for x in range(0, cs.TILE_WIDTH):
                # Expect non-white (line) pixels across the entire row
                self.assertFalse(cs.is_pixel_white(new_surface, x, y))

        # Test vertical lines at x=0 and x=99
        for x in [0, 99]:
            for y in range(10, 91):  # From row 10 to row 90 inclusive
                # Expect non-white (line) pixels down the entire column
                self.assertFalse(cs.is_pixel_white(new_surface, x, y))

    def test_two_full_characters_wide(self):
        stacking_surface_one = cs.draw_character("は")
        stacking_surface_two = cs.draw_character("は")

        surface = cs.create_blank(
            cairo.FORMAT_ARGB32, cs.TILE_WIDTH * 2, cs.TILE_HEIGHT
        )  # twice as wide
        ruled_surface = cs.apply_horizontal_rule(surface)
        boxed_surface = cs.apply_bounding_box(ruled_surface)
        boxed_surface = cs.apply_bounding_box(boxed_surface, x_offset=100)

        next_surface = cs.stack_surfaces(boxed_surface, stacking_surface_one)
        new_surface = cs.stack_surfaces(
            next_surface, stacking_surface_two, x_offset=100
        )

        # spot check surface is white
        self.assertTrue(cs.is_pixel_white(new_surface, 0, 0))
        self.assertTrue(cs.is_pixel_white(new_surface, 1, 0))
        # spot check certain points are non-white where char is drawn
        self.assertFalse(cs.is_pixel_white(new_surface, 25, 35))
        self.assertFalse(cs.is_pixel_white(new_surface, 60, 40))
        # and second char
        self.assertFalse(cs.is_pixel_white(new_surface, 125, 35))
        self.assertFalse(cs.is_pixel_white(new_surface, 160, 40))

        for y in [20, 80]:
            # dash on
            self.assertFalse(cs.is_pixel_white(new_surface, 0, y))
            self.assertFalse(cs.is_pixel_white(new_surface, 1, y))
            # dash off
            self.assertTrue(cs.is_pixel_white(new_surface, 2, y))
            self.assertTrue(cs.is_pixel_white(new_surface, 3, y))
            self.assertTrue(cs.is_pixel_white(new_surface, 4, y))
            self.assertTrue(cs.is_pixel_white(new_surface, 5, y))

        # Test horizontal lines at y=10 and y=90
        for y in [10, 90]:
            for x in range(0, cs.TILE_WIDTH * 2):  # twice as wide
                # Expect non-white (line) pixels across the entire row
                self.assertFalse(cs.is_pixel_white(new_surface, x, y))

        for y in range(10, 90):  # From row 10 to row 90 inclusive
            for x in [0, 99, 100, 199]:  # the four vertical lines drawn
                # Expect non-white (line) pixels down the entire column
                self.assertFalse(cs.is_pixel_white(new_surface, x, y))

    def test_two_full_characters_tall(self):
        stacking_surface_one = cs.draw_character("は")
        stacking_surface_two = cs.draw_character("は")

        surface = cs.create_blank(
            cairo.FORMAT_ARGB32, cs.TILE_WIDTH, cs.TILE_HEIGHT * 2
        )  # twice as wide

        ruled_surface = cs.apply_horizontal_rule(surface)
        ruled_surface = cs.apply_horizontal_rule(ruled_surface, y_offset=100)
        boxed_surface = cs.apply_bounding_box(ruled_surface)
        boxed_surface = cs.apply_bounding_box(boxed_surface, y_offset=100)

        next_surface = cs.stack_surfaces(boxed_surface, stacking_surface_one)
        new_surface = cs.stack_surfaces(
            next_surface, stacking_surface_two, y_offset=100
        )

        # spot check surface is white
        self.assertTrue(cs.is_pixel_white(new_surface, 0, 0))
        self.assertTrue(cs.is_pixel_white(new_surface, 1, 0))
        # spot check certain points are non-white where char is drawn
        self.assertFalse(cs.is_pixel_white(new_surface, 25, 35))
        self.assertFalse(cs.is_pixel_white(new_surface, 60, 40))
        # and second char
        self.assertFalse(cs.is_pixel_white(new_surface, 25, 135))
        self.assertFalse(cs.is_pixel_white(new_surface, 60, 140))

        for y in [120, 180]:
            # dash on
            self.assertFalse(cs.is_pixel_white(new_surface, 0, y))
            self.assertFalse(cs.is_pixel_white(new_surface, 1, y))
            # dash off
            self.assertTrue(cs.is_pixel_white(new_surface, 2, y))
            self.assertTrue(cs.is_pixel_white(new_surface, 3, y))
            self.assertTrue(cs.is_pixel_white(new_surface, 4, y))
            self.assertTrue(cs.is_pixel_white(new_surface, 5, y))

        # Test horizontal rules at y=10 and y=90
        for y in [10, 90, 110, 190]:
            for x in range(0, cs.TILE_WIDTH):  # twice as wide
                # Expect non-white (line) pixels across the entire row
                self.assertFalse(cs.is_pixel_white(new_surface, x, y))

        # Test vertical lines at x=0 and x=99
        for x in [0, 99]:
            for y in range(10, 90):  # From row 10 to row 90 inclusive
                # Expect non-white (line) pixels down the entire column
                self.assertFalse(cs.is_pixel_white(new_surface, x, y))
            for y in range(110, 190):  # From row 110 to row 190 inclusive
                # Expect non-white (line) pixels down the entire column
                self.assertFalse(cs.is_pixel_white(new_surface, x, y))


if __name__ == "__main__":
    unittest.main()
