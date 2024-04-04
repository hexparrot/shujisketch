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


def apply_horizontal_rule(surface):
    ctx = cairo.Context(surface)
    ctx.set_source_rgb(0.8, 0.8, 0.8)
    ctx.set_line_width(1)
    ctx.set_dash([2.0, 4.0])

    for y in [20, 80]:
        ctx.move_to(0, y)
        ctx.line_to(surface.get_width(), y)
        ctx.stroke()

    return surface
