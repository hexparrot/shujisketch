#!/usr/bin/python3

import char_surface as cs
import cairo
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

APP_TITLE = "しゅじsketch"


class DrawingArea(Gtk.DrawingArea):
    def __init__(self, initial_text=APP_TITLE):
        super().__init__()
        self.set_size_request(600, 200)
        self.connect("draw", self.on_draw)
        self.text = initial_text
        self.backing_store = None

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

    def on_draw(self, widget, cr):
        self.ensure_backing_store(widget)

        cr.set_source_surface(self.backing_store, 0, 0)
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
                APP_TITLE, font_size=144, tile_width=200, tile_height=200
            )
            self.backing_store = cs.apply_horizontal_rule(surface, rules=(40, 160))
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


def main():
    window = Gtk.Window(title=APP_TITLE)
    window.connect("destroy", Gtk.main_quit)

    drawing_area = DrawingArea()

    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    vbox.pack_start(drawing_area, True, True, 0)

    window.add(vbox)

    window.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
