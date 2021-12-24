"""
This is a helper library to minimise code duplication of the setup code and make users code much simpler
"""

import sys  # used to exit the program
import json  # used to parse the coordinates
import time  # used to get the current time and sleep


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


def get_coords_pixels():
    """Load the coordinates and create the neopixel interface."""
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
    """
    A class to help cap the frame rate. You shouldn't rely on the neopixel show method having a known delay.
    Use it like this

    with FrameManager(frame_time):  # frame_time should be something like 1/30 to get 30fps
        print("your frame code here")

    See template.py for a more full example.
    """
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


if __name__ == "__main__":
    print("matts_tree_helpers.py is not directly callable. Import it from your code.")
