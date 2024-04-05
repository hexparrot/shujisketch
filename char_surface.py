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


def create_blank(format, width, height):
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


def apply_horizontal_rule(surface):
    """
    Return a surface object with a newly applied horizontal rule
    and return the surface back.

    :param surface: A cairo.ImageSurface object.
    """
    ctx = cairo.Context(surface)
    ctx.set_source_rgb(0.8, 0.8, 0.8)
    ctx.set_line_width(1)
    ctx.set_dash([2.0, 4.0])

    for y in [20, 80]:
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


def draw_character(char):
    """
    Draw a character on a fully transparent surface and return it.

    :param char: the character to draw
    """
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
    import cairo

    # Step 1: Draw the character on a transparent background
    image = Image.new(
        "RGBA", (TILE_WIDTH, TILE_HEIGHT), (0, 0, 0, 0)
    )  # Use fully transparent background
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    draw.text(
        (10, 0), char, fill=(0, 0, 0, FONT_ALPHA), font=font
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
        data, cairo.FORMAT_ARGB32, TILE_WIDTH, TILE_HEIGHT, TILE_WIDTH * 4
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
