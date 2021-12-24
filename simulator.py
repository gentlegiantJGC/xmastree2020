"""
This is a visualiser for the neopixel library for those that just want to simulate the code.
It is a mostly drop-in replacement for the normal library.

Based on the simulator by DutChen18. Source: https://github.com/standupmaths/xmastree2020/pull/5/files

Changes:
Moves the matplotlib code to a new thread so that the updating code does not block the UI
Adds a method to set the pixel locations so that they are not hard coded
Made the axis proportional in size

Potential future work:
Consider adding support for pixel colour order.
    Unsure if the one Matt is running uses this

Usage:
You will need to import it like this.

try:
    # Try an import the real neopixel library
    import board
    import neopixel
except ImportError as e1:
    # If the real neopixel library cannot be imported try and import the simulator
    print(f"Failed to import board and neopixel. Trying the simulator.\n{e1}")
    try:
        from simulator import board, neopixel
    except ImportError as e2:
        # If the simulator failed to import, print the error and exit
        print(f"Failed to import the simulator. \n{e2}\nExiting.")
        sys.exit(1)


# construct the neopixel interface in the normal way
pixels = neopixel.NeoPixel(
    board.D18, len(coords), auto_write=False
)

# You will then need to set the location of each pixel.
# This is a custom method that does not exist in the real library.
# Call it like this to catch and ignore the error when run on the real hardware.
try:
    pixels.set_pixel_locations(coords)
except AttributeError:
    pass
"""

from typing import Iterable, Tuple
import sys
from threading import Thread
import time

import matplotlib
import matplotlib.pyplot as plt


# without this PyCharm displays it as an image that does not update.
matplotlib.use("TkAgg")
# set the style
plt.style.use("dark_background")


class board:
    D18 = None


class neopixel:
    class NeoPixel(Thread):
        def __init__(self, _, pixel_count, *args, **kwargs):
            super().__init__()
            self._pixels_temp = self._pixels = [(0, 0, 0)] * pixel_count
            self._locations = [[0] * pixel_count] * 3
            # track if the locations have changed so that the UI thread can update the view
            self._locations_changed = False
            # track if show has been called so the thread can push the changes
            self._show = True
            # True when the thread has finished so we can call sys.exit(0)
            self._exit = False
            # start the UI thread
            self.start()

        def set_pixel_locations(self, coords: Iterable[Tuple[int, int, int]]):
            """
            Custom method to set the location of each pixel.
            This does not exist in the normal neopixel library so you will need to call it like this
            try:
                pixels.set_pixel_locations(coords)
            except AttributeError:
                pass
            """
            coords = list(coords)
            if len(coords) != len(self._pixels_temp):
                raise ValueError(
                    "The number of coordinates must equal the number of pixels.\n"
                    f"Expected {len(self._pixels_temp)} got {len(coords)}"
                )
            if not all(
                len(c) == 3 and all(isinstance(a, (int, float)) for a in c)
                for c in coords
            ):
                raise ValueError(
                    "Coords must be of the form List[Tuple[int, int, int]]"
                )
            self._locations = list(zip(*coords))
            self._locations_changed = True

        def __setitem__(self, index, color):
            self._pixels_temp[index] = (
                color[1] / 255.0,
                color[0] / 255.0,
                color[2] / 255.0,
                1,
            )

        def show(self):
            if self._exit:
                sys.exit(0)
            self._pixels = self._pixels_temp.copy()
            self._show = True
            # The real library does some other things in this method which make it take longer.
            # Add a delay here to make the simulation play at the same speed.
            # I used the xmaslights-spin.py compared to Matt Parker's video to get this delay time
            time.sleep(0.027)

        def run(self):
            # create a figure
            fig = plt.figure()
            ax = fig.add_subplot(projection="3d")

            def exit_(evt):
                self._exit = True

            # exit python when the figure is closed
            fig.canvas.mpl_connect("close_event", exit_)

            while not self._exit:
                if self._show:
                    ax.cla()
                    ax.scatter(*self._locations, c=self._pixels)
                    self._show = False
                if self._locations_changed:
                    ax.set_box_aspect([max(ax) - min(ax) for ax in self._locations])
                    self._locations_changed = False
                plt.pause(1 / 100_000)
