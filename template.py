import sys  # used to exit the program
import json  # used to parse the coordinates

# Here are the libraries I am currently using:
import time
import random

# You are welcome to add any of these:
# import math
# import numpy
# import scipy
# import sys


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


def setup():
    """Load the coordinats and create the board"""
    with open("coords.txt") as fin:
        coords = list(map(json.loads, fin.readlines()))

    # set up the pixels (AKA 'LEDs')
    pixels = neopixel.NeoPixel(board.D18, len(coords), auto_write=False)
    try:
        pixels.set_pixel_locations(coords)
    except AttributeError:
        pass
    return coords, pixels


class FrameManager:
    def __init__(self, frame_time: float):
        self._frame_time = frame_time
        self._start_time = 0

    def __enter__(self):
        self._start_time = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # If the frame was processed in less time than frame_time then sleep for a bit
        dt = max(
            0.0, self._frame_time - (time.time() - self._start_time)
        )  # total frame time minus the elapsed time for the frame
        if dt:
            time.sleep(dt)


def template():
    # NOTE THE LEDS ARE GRB COLOUR (NOT RGB)

    # If you want to have user changeable values, they need to be entered from the command line
    # so import sys and use sys.argv[0] etc.
    # some_value = int(sys.argv[0])

    coords, pixels = setup()

    # YOU CAN EDIT FROM HERE DOWN

    frame_time = 1 / 30

    while True:
        # This handles waiting if the frame is processed quicker than frame_time
        with FrameManager(frame_time):
            # calculate the colour for each pixel
            for i in range(len(coords)):
                # random colour per LED per frame
                pixels[i] = tuple(random.randint(0, 255) for _ in range(3))

            # use the show() option as rarely as possible as it takes ages
            # do not use show() each time you change a LED but rather wait until you have changed them all
            pixels.show()


if __name__ == "__main__":
    template()
