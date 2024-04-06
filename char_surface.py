import cairo

# MODULE CONSTANTS
FONT_SIZE = 72
FONT_ALPHA = 127
FONT_PATH = "/usr/share/fonts/google-droid-sans-fonts/DroidSansJapanese.ttf"
TILE_WIDTH = 100
TILE_HEIGHT = 100


def is_pixel_white(surface, x, y):
    """
    Examine a surface object and return True if the x-y coordinate
    renders a white pixel, alpha channel notwithstanding

    :param surface: A cairo.ImageSurface object.
    :param x: x-coordinate
    :param y: y-coordinate
    """
    # Ensure coordinates are within the surface bounds
    if x < 0 or y < 0 or x >= surface.get_width() or y >= surface.get_height():
        raise ValueError("x or y is out of bounds.")

    # Access the surface's data
    data = surface.get_data()

    # Calculate the byte index of the pixel
    # Note: This assumes the format is ARGB32 and each pixel is 4 bytes
    stride = surface.get_stride()
    pixel_index = y * stride + x * 4

    # Extract ARGB components
    a = data[pixel_index + 3]
    r = data[pixel_index + 2]
    g = data[pixel_index + 1]
    b = data[pixel_index]

    # Check if the pixel is white (ignoring alpha)
    return r == g == b == 255


def create_blank(format, width=TILE_WIDTH, height=TILE_HEIGHT):
    """
    Return a surface object that is sized with user dimensions
    and is completely empty.

    :param format: A cairo.FORMAT definition.
    :param width: width of surface
    :param height: heigh of surface
    """
    surface = cairo.ImageSurface(format, width, height)
    # Create a white image for testing
    ctx = cairo.Context(surface)
    ctx.set_source_rgb(1, 1, 1)  # Set the color to white
    ctx.paint()
    return surface


def apply_horizontal_rule(surface, y_offset=0, rules=[20, 80]):
    """
    Return a surface object with a newly applied horizontal rule
    and return the surface back.

    :param surface: A cairo.ImageSurface object.
    """
    ctx = cairo.Context(surface)
    ctx.set_source_rgb(0.8, 0.8, 0.8)
    ctx.set_line_width(1)
    ctx.set_dash([2.0, 4.0])
    ctx.translate(0, y_offset)

    for y in rules:
        ctx.move_to(0, y)
        ctx.line_to(surface.get_width(), y)
        ctx.stroke()

    return surface


def apply_bounding_box(surface, x_offset=0, y_offset=0):
    """
    Draws a bounding box of 1px width on the given Cairo ImageSurface.
    The box is positioned with horizontal lines at rows 10 and 90, and
    vertical lines at columns 0 and 99. (max width, less than max height)

    :param surface: A cairo.ImageSurface object.
    :param x_offset: x-coordinate to translate drawing
    :param y_offset: y-coordinate to translate drawing
    """
    # Create a drawing context for the surface
    ctx = cairo.Context(surface)
    # apply an offset to the context
    ctx.translate(x_offset, y_offset)

    # Set the line width to 1px
    ctx.set_line_width(1)

    # Set the drawing color (Here it's set to black; RGBA: 0, 0, 0, 1)
    ctx.set_source_rgba(0, 0, 0, 1)

    # Move to the starting point of the top horizontal line
    ctx.move_to(0, 10)
    # Draw the top horizontal line
    ctx.line_to(99, 10)

    # Draw the right vertical line
    ctx.move_to(99, 10)
    ctx.line_to(99, 90)

    # Draw the bottom horizontal line
    ctx.line_to(0, 90)

    # Draw the left vertical line
    ctx.line_to(0, 10)

    # Stroke the path to draw the lines on the surface
    ctx.stroke()

    # Return the modified surface
    return surface


def draw_character(
    char,
    font_size=FONT_SIZE,
    font_path=FONT_PATH,
    font_alpha=FONT_ALPHA,
    tile_width=TILE_WIDTH,
    tile_height=TILE_HEIGHT,
):
    """
    Draw a character on a fully transparent surface and return it.

    :param char: the character to draw
    """
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
    import cairo

    def calculate_centering_offset(object_size):
        # Define offsets based on object size ranges
        if object_size <= 18:
            offset = 2
        elif object_size <= 36:
            offset = 5
        elif object_size <= 72:
            offset = 10
        else:
            # For sizes greater than 72
            offset = 15  # Default to 10

        return offset

    # Step 1: Draw the character on a transparent background
    image = Image.new(
        "RGBA", (tile_width, tile_height), (0, 0, 0, 0)
    )  # Use fully transparent background
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)
    draw.text(
        (calculate_centering_offset(font_size), 0),
        char,
        fill=(0, 0, 0, font_alpha),
        font=font,
    )  # Draw the text in white with semi-opacity for better contrast in grayscale conversion

    # Step 2: Convert the image to grayscale while preserving alpha
    gray_image = image.convert("LA")

    # Convert the PIL image (gray_image) to a NumPy array, then to BGRA for Cairo
    arr = np.array(gray_image)
    # Expand LA to RGBA by repeating the L value and combining with the A value
    bgra_arr = np.zeros((arr.shape[0], arr.shape[1], 4), dtype=np.uint8)
    bgra_arr[..., :3] = arr[..., 0:1]  # Set RGB to the L value
    bgra_arr[..., 3] = arr[..., 1]  # Set A value
    data = bgra_arr.flatten()

    # Step 3: Create a Cairo ImageSurface from the NumPy array data
    surface = cairo.ImageSurface.create_for_data(
        data, cairo.FORMAT_ARGB32, tile_width, tile_height, tile_width * 4
    )

    return surface


def stack_surfaces(base_layer, top_layer, x_offset=0, y_offset=0):
    """
    Stack two surfaces atop another.

    :param base_layer: A cairo.ImageSurface object.
    :param top_layer: A cairo.ImageSurface object.
    :param x_offset: x-coordinate to translate drawing
    :param y_offset: y-coordinate to translate drawing
    """
    cr = cairo.Context(base_layer)

    cr.set_source_surface(top_layer, x_offset, y_offset)
    cr.paint()

    return base_layer


def render_string(
    text_str,
    render_vertically=False,
    font_size=FONT_SIZE,
    font_path=FONT_PATH,
    font_alpha=FONT_ALPHA,
    tile_width=TILE_WIDTH,
    tile_height=TILE_HEIGHT,
):
    """
    Render a surface with a string of characters against a white bg.

    :param text_str: a string to print
    :param font_size: the font size
    :param font_path: absolute path to requested font TTF file
    :param font_alpha: alpha channel value of the text
    :param tile_width: width of each individual tile
    :param tile_height: height of each individual tile
    """
    tiles = [
        draw_character(
            c,
            font_size=font_size,
            font_path=font_path,
            font_alpha=font_alpha,
            tile_width=tile_width,
            tile_height=tile_height,
        )
        for c in text_str
    ]

    if render_vertically:
        surface = create_blank(
            cairo.FORMAT_ARGB32, tile_width, tile_height * len(tiles)
        )

        for i, tile in enumerate(tiles):
            surface = stack_surfaces(surface, tile, y_offset=tile_height * i)
    else:  # horizontal rendering default
        surface = create_blank(
            cairo.FORMAT_ARGB32, tile_width * len(tiles), tile_height
        )

        for i, tile in enumerate(tiles):
            surface = stack_surfaces(surface, tile, x_offset=tile_width * i)

    return surface


def extract_rectangle(original_surface, x, y, rect_width, rect_height):
    """
    Create a surface from an existing surface, duplicating its contents

    :param original_surface: the surface to copy from
    :param x: x offset to move capturing window
    :param y: y offset to move capturing window
    :param rect_width: width of the exporting surface rectangle
    :param rect_height: height of the exporting surface rectangle
    """
    # Create a new surface to hold the extracted rectangle
    new_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, rect_width, rect_height)
    # Set up a context for the new surface
    ctx = cairo.Context(new_surface)
    # Specify the original surface as the source, offset to align the desired rectangle
    ctx.set_source_surface(original_surface, -x, -y)
    # Paint the source surface onto the new surface
    ctx.paint()
    return new_surface


def white_pixels_match(surface1, surface2):
    """
    Check that an image shares all the same white pixels.

    Many surfaces from this module will have white backgrounds;
    this function allows easy equivalence testing, as any pixels
    that are not full-on (255,255,255) would make the resulting
    arrays not identical, providing an easy boolean comparison.

    :param surface1: reference surface
    :param surface2: compared surface
    """
    import numpy as np

    # Ensure surfaces have the same dimensions
    if (
        surface1.get_width() != surface2.get_width()
        or surface1.get_height() != surface2.get_height()
    ):
        return False

    # Access pixel data from surfaces
    data1 = surface1.get_data()
    data2 = surface2.get_data()
    # Convert data to NumPy arrays for comparison (assuming ARGB32 format)
    arr1 = np.frombuffer(data1, dtype=np.uint32).reshape(
        (surface1.get_height(), surface1.get_width())
    )
    arr2 = np.frombuffer(data2, dtype=np.uint32).reshape(
        (surface2.get_height(), surface2.get_width())
    )
    # Identify white pixels (0xFFFFFFFF for fully opaque white in ARGB32) (generates an array of bools)
    white1 = arr1 == 0xFFFFFFFF
    white2 = arr2 == 0xFFFFFFFF
    # Check if white pixel positions match in both surfaces
    return np.array_equal(white1, white2)
