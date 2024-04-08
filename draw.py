#!/usr/bin/python3

import char_surface as cs
import cairo
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

APP_TITLE = "しゅじsketch"


class DrawingArea(Gtk.DrawingArea):
    def __init__(
        self,
        initial_text=APP_TITLE,
        fontsize=cs.FONT_SIZE,
        tilesize=cs.TILE_WIDTH,
        rules=cs.RULES,
    ):
        super().__init__()
        self.TILESIZE = tilesize
        self.FONTSIZE = fontsize
        self.RULES = rules

        self.connect("draw", self.on_draw)
        self.backing_store = None
        self.surface = None

        self.paths = []  # Add this to store paths
        self.current_path = []  # Temporary storage for the current drawing path

        # Connect event handlers for mouse events
        self.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
        )
        self.connect("button-press-event", self.on_button_press)
        self.connect("motion-notify-event", self.on_motion_notify)
        self.connect("button-release-event", self.on_button_release)
        self.change_text("しゅじ")

    def change_text(self, text):
        self.backing_store = None
        self.text = text
        self.set_size_request(len(self.text) * self.TILESIZE, self.TILESIZE)

    def on_draw(self, widget, cr):
        if not self.backing_store:
            # Set the source to the desired color (RGBA)
            cr.set_source_rgba(1, 1, 1, 1)  # For white: (1, 1, 1, 1)
            # Paint the entire surface with the source color
            cr.paint()

        self.ensure_backing_store(widget)

        cr.set_source_surface(self.backing_store, 0, 0)
        cr.paint()

        if self.surface:
            cr.set_source_surface(self.surface, 0, 0)
            cr.paint()

        self.draw_paths(cr)  # Draw the user paths

    def on_button_press(self, widget, event):
        # Start a new path
        self.current_path = [(event.x, event.y)]

    def on_motion_notify(self, widget, event):
        # Add point to current path if drawing
        if self.current_path:
            self.current_path.append((event.x, event.y))

    def on_button_release(self, widget, event):
        # Finish the current path
        if self.current_path:
            self.paths.append(self.current_path)
            self.current_path = []
            self.queue_draw()

    def ensure_backing_store(self, widget):
        alloc = widget.get_allocation()
        width, height = alloc.width, alloc.height

        # Check if we need to (re)create the backing store
        if (
            self.backing_store is None
            or self.backing_store.get_width() != width
            or self.backing_store.get_height() != height
        ):
            surface = cs.render_string(
                self.text,
                font_size=self.FONTSIZE,
                tile_width=self.TILESIZE,
                tile_height=self.TILESIZE,
            )
            self.backing_store = cs.apply_horizontal_rule(surface, rules=self.RULES)
            cr = cairo.Context(self.backing_store)

    def draw_paths(self, cr):
        # Set drawing properties for user paths
        cr.set_source_rgb(0, 0, 0)  # Drawing in black
        cr.set_line_width(4)  # Example line width
        for path in self.paths:
            if path:
                cr.move_to(path[0][0], path[0][1])
                for x, y in path[1:]:
                    cr.line_to(x, y)
                cr.stroke()


class shuji(Gtk.Window):
    def __init__(self, fontsize=72, tilesize=100, rules=[20, 80], fulltext=[]):
        super().__init__(title=APP_TITLE)
        self.FONTSIZE = fontsize
        self.TILESIZE = tilesize
        self.RULES = rules

        from itertools import cycle

        self.TEXT = cycle(fulltext)

        # Create a VBox to stack the drawing area and the buttons vertically
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        # Initialize DrawingArea and pack it into the VBox
        self.drawing_area = DrawingArea(
            fontsize=self.FONTSIZE, tilesize=self.TILESIZE, rules=self.RULES
        )
        vbox.pack_start(self.drawing_area, True, True, 0)

        # Create a button box for the three buttons
        button_box = Gtk.Box(spacing=6)
        vbox.pack_start(button_box, False, True, 0)

        # Create and add buttons to the button box
        clear_button = Gtk.Button(label="Clear Writing")
        clear_button.connect("clicked", self.on_clear_clicked)
        button_box.pack_start(clear_button, True, True, 0)

        evaluate_button = Gtk.Button(label="Evaluate")
        evaluate_button.connect("clicked", self.on_evaluate_clicked)
        button_box.pack_start(evaluate_button, True, True, 0)

        reset_button = Gtk.Button(label="Reset Guide Text")
        reset_button.connect("clicked", self.on_reset_clicked)
        button_box.pack_start(reset_button, True, True, 0)

        next_button = Gtk.Button(label="Next Line")
        next_button.connect("clicked", self.on_next_clicked)
        button_box.pack_start(next_button, True, True, 0)

    def save_paths_to_surface(self, paths):
        # Assume WIDTH and HEIGHT are defined as the dimensions of the drawing area
        WIDTH, HEIGHT = (
            len(self.drawing_area.text) * self.TILESIZE,
            self.TILESIZE,
        )  # Example dimensions, adjust as necessary

        # Create a new surface and draw paths onto it
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
        cr = cairo.Context(surface)

        # Optionally set a white background if your paths are not exclusively black-and-white
        cr.set_source_rgb(1, 1, 1)  # White background
        cr.paint()

        # Set drawing color to black for the paths
        cr.set_source_rgb(0, 0, 0)  # Black
        cr.set_line_width(4)  # Example line width

        # Draw all paths from self.drawing_area.paths
        for path in self.drawing_area.paths:
            if path:
                cr.move_to(path[0][0], path[0][1])
                for x, y in path[1:]:
                    cr.line_to(x, y)
                cr.stroke()

        return surface

    # Button event handlers
    def on_clear_clicked(self, button):
        # Clear the drawing area of user paths
        self.drawing_area.paths = []
        self.drawing_area.current_path = []

    def on_evaluate_clicked(self, button):
        # Evaluate the drawing via ocr
        chars = []
        for i in range(len(self.drawing_area.text)):
            surface = self.save_paths_to_surface(self.drawing_area.paths)
            retval = cs.ocr_by_index(surface, i)
            try:
                if ord(retval) not in [92]:
                    chars.append(retval)
            except TypeError:
                # typeerror found if two chars in string.
                # should never be the case in ocr_by_index
                # so throw it away for a space
                chars.append(" ")

        newval = "".join(chars)
        surface = cs.render_string(
            newval,
            font_size=self.FONTSIZE,
            tile_width=self.TILESIZE,
            tile_height=self.TILESIZE,
        )

        surface = cs.apply_horizontal_rule(surface, rules=self.RULES)
        self.drawing_area.surface = surface
        self.drawing_area.queue_draw()

    def on_reset_clicked(self, button):
        # Reset the drawing to its original state
        surface = cs.render_string(
            self.drawing_area.text,
            font_size=self.FONTSIZE,
            tile_width=self.TILESIZE,
            tile_height=self.TILESIZE,
        )
        surface = cs.apply_horizontal_rule(surface, rules=self.RULES)
        self.drawing_area.surface = surface
        self.drawing_area.queue_draw()

    def on_next_clicked(self, button):
        # Reset the drawing to its original state
        self.drawing_area.paths = []
        self.drawing_area.current_path = []
        next_line = next(self.TEXT)
        self.drawing_area.change_text(next_line)


if __name__ == "__main__":
    line_parts = [
        "わたしは",  # watashi wa - I
        "わかりません、",  # wakarimasen - don't know,
        "わたしが",  # watashi ga - I (subject marker),
        "わかるのは",  # wakaru no wa - what I know is,
        "わたしが",  # watashi ga - I (subject marker),
        "わかること",  # wakaru koto - things that I understand
        "だけ",  # dake - only
        "です",  # desu - is (polite).
    ]

    app = shuji(fontsize=144, tilesize=200, rules=(40, 160), fulltext=line_parts)
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
