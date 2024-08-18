"""
This controller is used to render a 16 by 16 image on screen using
pygame. Reading it contents of a custom binary file.
"""
import os
import time
import pygame

from pathlib import Path
from .images import Image, ImageException


class Controller():
    """
    Pygame is used as a simulator to test the rendering
    """

    def __init__(self, directory):
        self.running = True
        self._reload = False

        self.directory = Path(directory)
        
        self._files = self.directory.glob('*.frame')
        self._array = [x[:] for x in [[(0, 0, 0)] * 16] * 16]
        self._delay_until = time.time()

        pygame.init()
        pygame.display.set_caption('frame simulator')
        self._display = pygame.display.set_mode((256, 256))


    def __getitem__(self, pos):
        return self._array[pos[0]][pos[1]]

    def __setitem__(self, pos, value):
        self._array[pos[0]][pos[1]] = value

    
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
        # catch close button
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.shutdown()
                exit(0)

        for y in range(16):
            for x in range(16):
                block = pygame.Rect(x * 16, y * 16, 16, 16)
                pygame.draw.rect(self._display, self._array[x][y], block)

        pygame.display.flip()


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
        pygame.display.quit()
        pygame.quit()
