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

    def on_draw(self, widget, cr):
        self.ensure_backing_store(widget)

        cr.set_source_surface(self.backing_store, 0, 0)
        cr.paint()

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
