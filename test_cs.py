import unittest
import cairo
import char_surface as cs


def is_nhocr_available():
    import shutil

    return shutil.which("nhocr") is not None


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

    def test_render_string(self):
        # bounding boxes, horizontal rule present

        # evaluate when written horiztonally
        text_str = "こんにちわ"
        surface = cs.render_string(text_str)
        self.assertEqual(surface.get_width(), 500)
        self.assertEqual(surface.get_height(), 100)

        tiles = [cs.draw_character(c) for c in text_str]

        for i, t in enumerate(tiles):
            blank_surface = cs.create_blank(
                cairo.FORMAT_ARGB32, cs.TILE_WIDTH, cs.TILE_HEIGHT
            )
            new_tile = cs.stack_surfaces(blank_surface, tiles[i])
            extracted = cs.extract_rectangle(
                surface, i * cs.TILE_WIDTH, 0, cs.TILE_WIDTH, cs.TILE_HEIGHT
            )

            self.assertTrue(cs.white_pixels_match(extracted, new_tile))

        # evaluate when written vertically
        text_str = "こんにちわ"
        surface = cs.render_string(text_str, render_vertically=True)
        self.assertEqual(surface.get_width(), 100)
        self.assertEqual(surface.get_height(), 500)

        tiles = [cs.draw_character(c) for c in text_str]

        for i, t in enumerate(tiles):
            blank_surface = cs.create_blank(
                cairo.FORMAT_ARGB32, cs.TILE_WIDTH, cs.TILE_HEIGHT
            )
            new_tile = cs.stack_surfaces(blank_surface, tiles[i])
            extracted = cs.extract_rectangle(
                surface, 0, i * cs.TILE_HEIGHT, cs.TILE_WIDTH, cs.TILE_HEIGHT
            )

            self.assertTrue(cs.white_pixels_match(extracted, new_tile))

    def test_render_at_half_size(self):
        text_str = "こんにちわ"
        adjusted_font_size = 36
        adjusted_tile_size = 50
        surface = cs.render_string(
            text_str,
            font_size=adjusted_font_size,
            tile_width=adjusted_tile_size,
            tile_height=adjusted_tile_size,
        )
        # Check width and height dimensions
        self.assertEqual(surface.get_width(), adjusted_tile_size * len(text_str))
        self.assertEqual(surface.get_height(), adjusted_tile_size)

        # get an imagesurface for all characters
        tiles = [
            cs.draw_character(
                c,
                font_size=adjusted_font_size,
                tile_width=adjusted_tile_size,
                tile_height=adjusted_tile_size,
            )
            for c in text_str
        ]

        # in order, place these surfaces onto a single blank surface, as tiles
        for i, t in enumerate(tiles):
            blank_surface = cs.create_blank(
                cairo.FORMAT_ARGB32, adjusted_tile_size, adjusted_tile_size
            )
            new_tile = cs.stack_surfaces(blank_surface, tiles[i])
            extracted = cs.extract_rectangle(
                surface,
                i * adjusted_tile_size,  # x-offset scales here
                0,  # y-offset unchanged
                adjusted_tile_size,
                adjusted_tile_size,
            )

            # asserts that placement and extraction are pixel-perfect
            self.assertTrue(cs.white_pixels_match(extracted, new_tile))

    def test_render_at_double_size(self):
        text_str = "こんにちわ"
        adjusted_font_size = 144
        adjusted_tile_size = 200
        surface = cs.render_string(
            text_str,
            font_size=adjusted_font_size,
            tile_width=adjusted_tile_size,
            tile_height=adjusted_tile_size,
        )
        # Check width and height dimensions
        self.assertEqual(surface.get_width(), adjusted_tile_size * len(text_str))
        self.assertEqual(surface.get_height(), adjusted_tile_size)

        # get an imagesurface for all characters
        tiles = [
            cs.draw_character(
                c,
                font_size=adjusted_font_size,
                tile_width=adjusted_tile_size,
                tile_height=adjusted_tile_size,
            )
            for c in text_str
        ]

        # in order, place these surfaces onto a single blank surface, as tiles
        for i, t in enumerate(tiles):
            blank_surface = cs.create_blank(
                cairo.FORMAT_ARGB32, adjusted_tile_size, adjusted_tile_size
            )
            new_tile = cs.stack_surfaces(blank_surface, tiles[i])
            extracted = cs.extract_rectangle(
                surface,
                i * adjusted_tile_size,  # x-offset scales here
                0,  # y-offset unchanged
                adjusted_tile_size,
                adjusted_tile_size,
            )

            # asserts that placement and extraction are pixel-perfect
            self.assertTrue(cs.white_pixels_match(extracted, new_tile))

    def test_save_surface_to_pgm(self):
        import os

        text_str = "こんにちわ"
        adjusted_font_size = 144
        adjusted_tile_size = 200
        surface = cs.render_string(
            text_str,
            font_size=adjusted_font_size,
            tile_width=adjusted_tile_size,
            tile_height=adjusted_tile_size,
        )

        file_path = "sample_surface.pgm"
        cs.surface_to_pgm(surface, file_path)

        # Check if the file exists
        self.assertTrue(os.path.exists(file_path), "File does not exist.")

        # Open the file and check the first two bytes for the PPM magic number
        with open(file_path, "rb") as file:
            magic_number = file.read(2).decode("ascii")
            self.assertIn(magic_number, ["P2", "P5"], "File is not a valid PPM file.")

    @unittest.skip
    def test_perfect_font_reading(self):

        # Define a mapping of visually similar characters
        # also can be used to just suppress bad matches, bandaid
        # left-hand side is ocr result, right side is character fed to ocr
        visually_similar_characters = {
            "あ": ["ぁ"],
            "う": ["ぅ"],
            "え": ["ぇ"],
            "お": ["ぉ"],
            "L`": ["ぃ"],  # nonpermissible failure
            "L◆": ["ぃ", "い"],  # nonpermissible failure
            "カヽ": ["か"],
            "カヾ": ["が"],
            "<": ["く"],  # nonpermissible failure
            "き": ["さ"],  # nonpermissible failure
            "ぎ": ["ざ"],  # nonpermissible failure
            "つ": ["っ"],
            "｜こ": ["に"],  # nonpermissible failure
            "｜ま": ["は", "ば", "ぱ"],  # nonpermissible failure
            "づヽ": ["ふ"],  # nonpermissible failure
            "づ〈": ["ぷ"],  # nonpermissible failure
            "ヘ": ["へ"],
            "ベ": ["べ"],
            "や": ["ゃ"],
            "ゆ": ["ゅ"],
            "よ": ["ょ"],
            "V": ["り"],  # nonpermissible failure
            "わ": ["ゎ"],
            "": ["ゔ", "ゕ", "ゖ"],
        }

        def assertVisuallySimilar(actual, expected, msg=None):
            # Normalize newline characters to handle cases like 'あ\n' != 'ぁ'
            actual = actual.strip()
            expected = expected.strip()

            # Check for direct equality
            if actual == expected:
                return

            # Check for visual similarity
            for key, values in visually_similar_characters.items():
                if (actual == key and expected in values) or (
                    expected == key and actual in values
                ):
                    print("visual mismatch ignored:", actual, "vs", expected)
                    return  # means it wont hit fail, and doesnt count as a tested unittest

            # If not equal or visually similar, raise an AssertionError
            self.fail(
                self._formatMessage(
                    msg,
                    f"OCR result: '{actual}' is not visually similar to expected: '{expected}'",
                )
            )

        # Create a list of Hiragana characters from their Unicode code points
        hiragana_chars = [chr(i) for i in range(0x3041, 0x3097)]
        # Optionally, add iteration marks
        hiragana_chars.append(chr(0x309D))  # ゝ
        hiragana_chars.append(chr(0x309E))  # ゞ

        # Iterate through the list of Hiragana characters
        for char in hiragana_chars:
            surface = cs.render_string(
                char,
                font_size=144,
                tile_width=200,
                tile_height=200,
                font_alpha=255,
            )

            file_path = "sample_surface.pgm"
            cs.surface_to_pgm(surface, file_path)
            retval = cs.ocr(file_path)
            assertVisuallySimilar(
                retval, char, f"ocr result: {retval} expected: {char}"
            )

    @unittest.skipIf(not is_nhocr_available(), "nhocr not found in path, skipping test")
    def test_get_candidate_readings(self):
        # "｜こ": ["に"],  # nonpermissible failure
        output = """# Character candidates table
#   produced by: NHocr - Japanese OCR  v0.22
IMG	0
R	1	に	0	0	2.2526079e+00
R	2	仁	0	0	2.8243349e+00
R	3	c	0	0	3.2934342e+00
R	4	k	0	0	3.3655533e+00
R	5	K	0	0	3.3674219e+00
R	6	C	0	0	3.4016937e+00
R	7	た	0	0	3.5073901e+00
R	8	【	0	0	3.5609170e+00
R	9	じ	0	0	3.5680108e+00
R	10	ヒ	0	0	3.5937597e+00"""

        candidate_data = cs.parse_nhocr_output(output)
        # Check that the result is a list
        self.assertIsInstance(candidate_data, list, "The result should be a list.")

        # Check that each item in the list is a dictionary with the specified keys
        for item in candidate_data:
            self.assertIsInstance(
                item, dict, "Each item in the result should be a dictionary."
            )
            self.assertTrue(
                all(key in item for key in ["rank", "character", "score"]),
                "Each dictionary must contain 'rank', 'character', and 'score' keys.",
            )

        for idx, item in enumerate(candidate_data):
            self.assertEqual(candidate_data[idx]["rank"], idx + 1)

        self.assertEqual(candidate_data[0]["character"], "に")
        self.assertAlmostEqual(
            candidate_data[0]["score"],
            float(2.2526079e00),
            places=7,
            msg="The values are not close enough.",
        )

    @unittest.skipIf(not is_nhocr_available(), "nhocr not found in path, skipping test")
    def test_single_char_reading(self):
        target_char = "に"
        surface = cs.render_string(
            target_char,
            font_size=144,
            tile_width=200,
            tile_height=200,
            font_alpha=255,
        )

        file_path = "sample_surface.pgm"
        cs.surface_to_pgm(surface, file_path)

        retval = cs.ocr(file_path, single_char_reading=True)
        self.assertEqual(retval, target_char)

    @unittest.skipIf(not is_nhocr_available(), "nhocr not found in path, skipping test")
    def test_line_cleaning(self):
        text_str = "こんにちわ"
        surface = cs.render_string(
            text_str,
            font_size=144,
            tile_width=200,
            tile_height=200,
            font_alpha=255,
        )

        file_path = "sample_surface.pgm"
        cs.surface_to_pgm(surface, file_path)

        retval = cs.ocr(file_path)
        # 'こ ん に ちわ' != 'こんにちわ'
        self.assertEqual(retval, text_str)

    @unittest.skipIf(not is_nhocr_available(), "nhocr not found in path, skipping test")
    def test_line_correction_char_count(self):
        text_str = "にに"
        surface = cs.render_string(
            text_str,
            font_size=72,
            tile_width=100,
            tile_height=100,
            font_alpha=255,
        )

        file_path = "sample_surface.pgm"
        cs.surface_to_pgm(surface, file_path)

        retval = cs.ocr(file_path, known_translation=text_str)
        # '|=|=' != 'にに'
        self.assertEqual(retval, text_str)

    @unittest.skipIf(not is_nhocr_available(), "nhocr not found in path, skipping test")
    def test_line_correction_char_count_half_size(self):
        text_str = "にに"
        surface = cs.render_string(
            text_str,
            font_size=36,
            tile_width=50,
            tile_height=50,
            font_alpha=255,
        )

        file_path = "sample_surface.pgm"
        cs.surface_to_pgm(surface, file_path)

        retval = cs.ocr(file_path, known_translation=text_str)
        # '|=|=' != 'にに'
        self.assertEqual(retval, text_str)

    @unittest.skipIf(not is_nhocr_available(), "nhocr not found in path, skipping test")
    def test_line_correction_char_count_double_size(self):
        text_str = "にに"
        surface = cs.render_string(
            text_str,
            font_size=144,
            tile_width=200,
            tile_height=200,
            font_alpha=255,
        )

        file_path = "sample_surface.pgm"
        cs.surface_to_pgm(surface, file_path)

        retval = cs.ocr(file_path, known_translation=text_str)
        # '|=|=' != 'にに'
        self.assertEqual(retval, text_str)

    @unittest.skipIf(not is_nhocr_available(), "nhocr not found in path, skipping test")
    def test_line_correction_char_count_vertical(self):
        text_str = "にに"
        surface = cs.render_string(
            text_str,
            font_size=72,
            tile_width=100,
            tile_height=100,
            font_alpha=255,
            render_vertically=True,
        )

        file_path = "sample_surface.pgm"
        cs.surface_to_pgm(surface, file_path)

        retval = cs.ocr(file_path, known_translation=text_str, render_vertically=True)
        # '|=|=' != 'にに'
        self.assertEqual(retval, text_str)

    @unittest.skipIf(not is_nhocr_available(), "nhocr not found in path, skipping test")
    def test_line_correction_char_count_half_size_vertical(self):
        text_str = "にに"
        surface = cs.render_string(
            text_str,
            font_size=36,
            tile_width=52,
            tile_height=52,
            font_alpha=255,
            render_vertically=True,
        )

        file_path = "sample_surface.pgm"
        cs.surface_to_pgm(surface, file_path)

        retval = cs.ocr(file_path, known_translation=text_str, render_vertically=True)
        # '|=|=' != 'にに'
        self.assertEqual(retval, text_str)

    @unittest.skipIf(not is_nhocr_available(), "nhocr not found in path, skipping test")
    def test_line_correction_char_count_double_size_vertical(self):
        text_str = "にに"
        surface = cs.render_string(
            text_str,
            font_size=144,
            tile_width=200,
            tile_height=200,
            font_alpha=255,
            render_vertically=True,
        )

        file_path = "sample_surface.pgm"
        cs.surface_to_pgm(surface, file_path)

        retval = cs.ocr(file_path, known_translation=text_str, render_vertically=True)
        # '|=|=' != 'にに'
        self.assertEqual(retval, text_str)

    @unittest.skipIf(not is_nhocr_available(), "nhocr not found in path, skipping test")
    def test_line_translation_with_provided_spaces(self):
        text_str = "も の が た り"
        surface = cs.render_string(
            text_str,
            font_size=144,
            tile_width=200,
            tile_height=200,
            font_alpha=255,
        )

        file_path = "sample_surface.pgm"
        cs.surface_to_pgm(surface, file_path)

        retval = cs.ocr(file_path, known_translation=text_str)
        self.assertEqual(retval, text_str)

    @unittest.skipIf(not is_nhocr_available(), "nhocr not found in path, skipping test")
    def test_spot_check_character_by_index(self):
        text_str = "ものがたり"
        surface = cs.render_string(
            text_str,
            font_size=72,
            tile_width=100,
            tile_height=100,
            font_alpha=255,
        )

        self.assertEqual(cs.ocr_by_index(surface, 0), "も")
        self.assertEqual(cs.ocr_by_index(surface, 1), "の")
        self.assertEqual(cs.ocr_by_index(surface, 2), "が")
        self.assertEqual(cs.ocr_by_index(surface, 3), "た")
        self.assertEqual(cs.ocr_by_index(surface, 4), "り")

        surface = cs.render_string(
            text_str,
            font_size=144,
            tile_width=200,
            tile_height=200,
            font_alpha=255,
        )

        self.assertEqual(cs.ocr_by_index(surface, 0), "も")
        self.assertEqual(cs.ocr_by_index(surface, 1), "の")
        self.assertEqual(cs.ocr_by_index(surface, 2), "が")
        self.assertEqual(cs.ocr_by_index(surface, 3), "た")
        self.assertEqual(cs.ocr_by_index(surface, 4), "り")

        surface = cs.render_string(
            text_str,
            font_size=36,
            tile_width=50,
            tile_height=50,
            font_alpha=255,
        )

        self.assertEqual(cs.ocr_by_index(surface, 0), "も")
        self.assertEqual(cs.ocr_by_index(surface, 1), "の")
        self.assertEqual(cs.ocr_by_index(surface, 2), "が")
        self.assertEqual(cs.ocr_by_index(surface, 3), "た")
        self.assertEqual(cs.ocr_by_index(surface, 4), "り")

    @unittest.skipIf(not is_nhocr_available(), "nhocr not found in path, skipping test")
    def test_spot_check_character_by_index_vertical(self):
        text_str = "ものがたり"
        surface = cs.render_string(
            text_str,
            font_size=72,
            tile_width=100,
            tile_height=100,
            font_alpha=255,
            render_vertically=True,
        )

        self.assertEqual(cs.ocr_by_index(surface, 0), "も")
        self.assertEqual(cs.ocr_by_index(surface, 1), "の")
        self.assertEqual(cs.ocr_by_index(surface, 2), "が")
        self.assertEqual(cs.ocr_by_index(surface, 3), "た")
        self.assertEqual(cs.ocr_by_index(surface, 4), "り")

        surface = cs.render_string(
            text_str,
            font_size=144,
            tile_width=200,
            tile_height=200,
            font_alpha=255,
            render_vertically=True,
        )

        self.assertEqual(cs.ocr_by_index(surface, 0), "も")
        self.assertEqual(cs.ocr_by_index(surface, 1), "の")
        self.assertEqual(cs.ocr_by_index(surface, 2), "が")
        self.assertEqual(cs.ocr_by_index(surface, 3), "た")
        self.assertEqual(cs.ocr_by_index(surface, 4), "り")

        surface = cs.render_string(
            text_str,
            font_size=36,
            tile_width=50,
            tile_height=50,
            font_alpha=255,
            render_vertically=True,
        )

        self.assertEqual(cs.ocr_by_index(surface, 0), "も")
        self.assertEqual(cs.ocr_by_index(surface, 1), "の")
        self.assertEqual(cs.ocr_by_index(surface, 2), "が")
        self.assertEqual(cs.ocr_by_index(surface, 3), "た")
        self.assertEqual(cs.ocr_by_index(surface, 4), "り")

    def test_bounding_box_tight_dimensions(self):
        import tempfile

        def calculate_rectangle_area(rect):
            """
            Calculate the area of a rectangle given its coordinates.

            :param rect: A tuple of (left, top, right, bottom) coordinates.
            :return: The area of the rectangle.
            """
            # Unpack the coordinates
            left, top, right, bottom = rect

            # Calculate width and height
            width = right - left
            height = bottom - top

            # Calculate and return area
            return width * height

        char_pair = [
            ("ぁ", "あ"),
            ("ぅ", "う"),
            ("ぇ", "え"),
            ("ぉ", "お"),
            ("っ", "つ"),
            ("ゃ", "や"),
            ("ゅ", "ゆ"),
            ("ょ", "よ"),
            ("ゎ", "わ"),
        ]

        for a, b in char_pair:
            surface_sm = cs.render_string(
                a,
                font_size=144,
                tile_width=200,
                tile_height=200,
                font_alpha=255,
            )

            surface_nm = cs.render_string(
                b,
                font_size=144,
                tile_width=200,
                tile_height=200,
                font_alpha=255,
            )

        with tempfile.NamedTemporaryFile(delete=True, suffix=".pgm") as temp_file_sm:
            # Use the temporary file's name
            cs.surface_to_pgm(surface_sm, temp_file_sm.name)

            # Create another temporary file
            with tempfile.NamedTemporaryFile(
                delete=True, suffix=".pgm"
            ) as temp_file_nm:
                # Use the second temporary file's name
                cs.surface_to_pgm(surface_nm, temp_file_nm.name)

                # Since we are within the context, the file exists and we can read from it
                bbox1 = cs.find_tight_bounding_box(temp_file_sm.name)
                bbox2 = cs.find_tight_bounding_box(temp_file_nm.name)

                # small will always be less than the large! always! this is area
                self.assertLess(
                    calculate_rectangle_area(bbox1), calculate_rectangle_area(bbox2)
                )

                # small will always be less than the large! always! here is proportion
                self.assertLess(
                    cs.find_rectangle_proportion(bbox1),
                    cs.find_rectangle_proportion(bbox2),
                )

    def test_guess_character_size(self):
        def get_bbox(char):
            import tempfile

            with tempfile.NamedTemporaryFile(
                delete=True, suffix=".pgm"
            ) as temp_file_sm:
                # Use the temporary file's name
                surface_sm = cs.render_string(
                    char,
                    font_size=144,
                    tile_width=200,
                    tile_height=200,
                    font_alpha=255,
                )
                cs.surface_to_pgm(surface_sm, temp_file_sm.name)
                return cs.find_tight_bounding_box(temp_file_sm.name)

        # List of small to large character pairs
        char_pairs = [
            ("ぁ", "あ"),
            ("ぅ", "う"),
            ("ぇ", "え"),
            ("ぉ", "お"),
            ("っ", "つ"),
            ("ゃ", "や"),
            ("ゅ", "ゆ"),
            ("ょ", "よ"),
            ("ゎ", "わ"),
        ]

        # Iterate through each pair and test classification
        for small_char, large_char in char_pairs:
            with self.subTest(char=small_char):
                self.assertEqual(
                    cs.guess_character_size(get_bbox(small_char)),
                    "small",
                    f"{small_char} should be classified as 'small'",
                )

            with self.subTest(char=large_char):
                self.assertEqual(
                    cs.guess_character_size(get_bbox(large_char)),
                    "large",
                    f"{large_char} should be classified as 'large'",
                )

    def test_convert_black_text_to_green(self):
        import numpy as np

        surface = cs.draw_character(
            "よ",
            font_size=72,
            tile_width=100,
            tile_height=100,
        )
        transformed_surface = cs.paint_grayscale_to_green(surface)

        # Check pixel colors
        width, height = (
            transformed_surface.get_width(),
            transformed_surface.get_height(),
        )
        data = np.ndarray(
            shape=(height, width, 4),
            dtype=np.uint8,
            buffer=transformed_surface.get_data(),
        )

        # Assert that we have green pixels where there was text
        for y in range(height):
            for x in range(width):
                r, g, b, a = data[y, x]
                if a > 0:  # Where there was text, expecting green
                    self.assertGreater(g, 0)
                    self.assertEqual(r, 0)
                    self.assertEqual(b, 0)
                else:  # Where there was no text, expecting full transparency
                    self.assertEqual(a, 0)


if __name__ == "__main__":
    unittest.main()
