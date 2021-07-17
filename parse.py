"""
Simple command line tool to parse images to the frame format
"""
import math
import struct
import argparse
import gif

from pathlib import Path
from common.images import ImageException


class Frame():
    """
    Frames as part of an image
    """

    def __init__(self, delay, pixels):
        self.packet = b''
        self.delay = delay

        for color in pixels:
            self.packet += struct.pack('BBB', *color)


class Image():
    """
    Load image from file, perform some basic checks

    Attributes
    ----------
    url : str
        the path to the image file
    """
    def __init__(self, path):
        self.image = open(path, 'rb')       
        self.frames = []

        self.reader = gif.Reader()
        self.reader.feed(self.image.read())

        self.loop_count = 1

        if not self.reader.has_screen_descriptor():
            raise ImageException('No valid image descripter')

        if self.reader.width != 16:
            raise ImageException('Image width incorrect')

        if self.reader.height != 16:
            raise ImageException('Image height incorrect')
        
        self.__read_frames()


    def store(self, path, version):
        version = 1 if version is None else version

        if version not in range(1, 2):
            raise ImageException('unsupported version')

        with open(path, 'wb') as f:
            f.write(struct.pack('!7sB', b'\x87\x46\x52\x41\x4d\x45\x0A', version))

            if version == 1: 
                f.write(struct.pack('!4x BBBB', self.reader.width, self.reader.height, len(self.frames), self.loop_count))

                for frame in self.frames:
                    f.write(struct.pack('!H', int(frame.delay)))
                    f.write(frame.packet)
            
            elif version == 2:
                f.write(struct.pack('!4x BBBB', self.reader.width, self.reader.height, len(self.frames), self.loop_count))

                # TODO color table

        print(f'wrote {path}')


    def __read_frames(self):

        # initialize first pixel array with background color
        pixels = [self.reader.color_table[self.reader.background_color]] * (16*16)
        transparent_color = None
        delay = 0.01

        for block in self.reader.blocks:

            # read repeat count only once
            if isinstance(block, (gif.AnimationExtension, gif.NetscapeExtension)):
                if block.loop_count is not None:
                    self.loop_count = block.loop_count

            # read delay before reading image
            elif isinstance(block, gif.GraphicControlExtension):
                delay = block.delay_time * 10

                if block.has_transparent or block.transparent_color != 0:
                    transparent_color = block.transparent_color

            elif isinstance(block, gif.Image):
                for index, pixel in enumerate(block.get_pixels()):

                    if pixel == transparent_color:
                        continue
            
                    if len(block.color_table) > 0:
                        pixels[self.transpose(index, block)] = block.color_table[pixel]
                    elif len(self.reader.color_table) > 0:
                        pixels[self.transpose(index, block)] = self.reader.color_table[pixel]
                    else:
                        raise ImageException('color_table is incomplete')

                frame = Frame(delay, pixels)
                self.frames.append(frame)

    @staticmethod
    def transpose(index, image):
        """
        Use index and frame dimension to calculate index based on a (16,16) canvas
        Not all frames start at (0,0)
        """
        row = math.floor(index / image.width)
        return (index % image.width + image.left) + (row + image.top) * 16

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Frame parser')
    parser.add_argument('image', help='image to parse')
    parser.add_argument('--output', '-o', help='output directory')

    parser.add_argument('--version', '-v', type=int, help='frame file version')
    args = parser.parse_args()

    file = Path(args.image)
    image = Image(file)

    destination = Path(args.output) if args.output else Path(file.parent)
    if not destination.is_dir():
        destination = Path(destination.parent) / f'{destination.stem}.frame'
    else:
        destination = destination / f'{file.stem}.frame'

    image.store(destination, args.version)

    exit(0)
