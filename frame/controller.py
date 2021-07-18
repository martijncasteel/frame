"""
This controller is used to render a 16 by 16 image on screen using
pygame. Reading it contents of a custom binary file.
"""
import os
import time

import board
import neopixel

from pathlib import Path
from common.images import Image, ImageException


class Controller():
    """
    Pygame is used as a simulator to test the rendering
    """

    def __init__(self, directory, brightness=5):
        self.running = True
        self._reload = False

        self.directory = Path(directory)
        
        self._files = self.directory.glob('*.frame')
        self._array = neopixel.NeoPixel(board.D18, 256, brightness=brightness/255, auto_write=False)
        self._delay_until = time.time()


    def __getitem__(self, pos):
        return self._array[self.__alternate(*pos)]

    def __setitem__(self, pos, value):
        self._array[self.__alternate(*pos)] = value

    
    def run(self):
        self._reload = False

        for file in self._files:
            try:
                with file.open(mode='rb') as f:

                    image = Image(f)
                    image.display(self)

            except ImageException as exception:
                print(exception)
                continue

            except FileNotFoundError as exception:
                print(f'file not found: {exception.filename}')
                continue

            if self._reload:
                return


    def draw(self):
        self._array.show()
        

    def sleep(self, next_showing):
        seconds = self._delay_until - time.time()
        
        if seconds > 0:
            time.sleep(seconds)

        self._delay_until = next_showing + time.time()


    def reload(self, verbose=False):
        if verbose:
            print('reloading files..')
        
        self._files = self.directory.glob('*.frame')
        self._reload = True

    def shutdown(self):
        self._array.fill((0, 0, 0))
        self._array.show()


    @staticmethod
    def __alternate(x, y):
        index = y * 16

        if y % 2 == 0:
            index += 15 - x
        else:
            index += x
        
        return index