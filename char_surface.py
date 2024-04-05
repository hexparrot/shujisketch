import cairo


def is_pixel_white(surface, x, y):
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
    surface = cairo.ImageSurface(format, width, height)
    # Create a white image for testing
    ctx = cairo.Context(surface)
    ctx.set_source_rgb(1, 1, 1)  # Set the color to white
    ctx.paint()
    return surface


def draw_horizontal_rule(surface):
    ctx = cairo.Context(surface)
    ctx.set_source_rgb(0.8, 0.8, 0.8)
    ctx.set_line_width(1)
    ctx.set_dash([2.0, 4.0])

    for y in [20, 80]:
        ctx.move_to(0, y)
        ctx.line_to(surface.get_width(), y)
        ctx.stroke()

    return surface


def draw_bounding_box(surface):
    """
    Draws a bounding box of 1px width on the given Cairo ImageSurface.
    The box is positioned with horizontal lines at rows 10 and 90, and
    vertical lines at columns 0 and 99.

    :param surface: A cairo.ImageSurface object.
    """
    # Create a drawing context for the surface
    ctx = cairo.Context(surface)

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
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np

    background = Image.new("RGBA", (100, 100), (255, 255, 255, 255))
    image = Image.new("RGBA", (100, 100), (255, 255, 255, 0))  # Transparent background
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(
        "/usr/share/fonts/google-droid-sans-fonts/DroidSansJapanese.ttf", 72
    )
    draw.text(
        (10, 0), char, fill=(0, 0, 0, 127), font=font
    )  # Black text, 10 offset to center

    # Convert the PIL image to a NumPy array, then to BGRA for Cairo
    arr = np.array(image)[:, :, [2, 1, 0, 3]]  # Convert RGBA to BGRA
    data = arr.astype(np.uint8).flatten()

    # Create a Cairo ImageSurface from the NumPy array data
    surface = cairo.ImageSurface.create_for_data(
        data, cairo.FORMAT_ARGB32, 100, 100, 100 * 4
    )

    return surface


def stack_surfaces(base_layer, top_layer):
    cr = cairo.Context(base_layer)

    cr.set_source_surface(top_layer, 0, 0)
    cr.paint()

    return base_layer
