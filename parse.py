"""
Simple command line tool to parse images to the frame format
"""

import argparse
import math
import struct
import gif

from pathlib import Path
from common.images import ImageException

def create_from_gif(path, destination, version):
    """Load gif file for parsing and store it as a .frame file"""

    def read_gif_frames(reader):

        def read_frame(pixels, delay):
            packet = b''

            for color in pixels:
                packet += struct.pack('BBB', *color)

            return (packet, int(delay))

        # initialize first pixel array with background color
        pixels = [reader.color_table[reader.background_color]] * (16*16)
        frames =[]
        transparent_color = None
        loop_count = 1
        delay = 0.01

        for block in reader.blocks:

            # read repeat count only once
            if isinstance(block, (gif.AnimationExtension, gif.NetscapeExtension)):
                if loop_count is not None:
                    loop_count = block.loop_count

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
                        pixels[transpose(index, block)] = block.color_table[pixel]
                    elif len(reader.color_table) > 0:
                        pixels[transpose(index, block)] = reader.color_table[pixel]
                    else:
                        raise ImageException('color_table is incomplete')

                frame = read_frame(pixels, delay)
                frames.append(frame)
        
        return frames, (reader.width, reader.height, len(frames), loop_count)


    def store(path, frames, version, header):
        if version not in range(1, 2):
            raise ImageException('unsupported version')

        if not path.is_dir():
            destination = Path(path.parent) / f'{path.stem}.frame'
        else:
            destination = path / f'{path.stem}.frame'

        with open(destination, 'wb') as f:
            f.write(struct.pack('!7sB', b'\x87\x46\x52\x41\x4d\x45\x0A', version))

            if version == 1: 
                f.write(struct.pack('!4x BBBB', *header))

                for packet, delay in frames:
                    f.write(struct.pack('!H', delay))
                    f.write(packet)
            
            elif version == 2:
                f.write(struct.pack('!4x BBBB', *header))

                # TODO color table listing all colors first, and use index to point to the color

        print(f'wrote {destination}')

    file = open(path, 'rb')         
    reader = gif.Reader()
    reader.feed(file.read())

    if not reader.has_screen_descriptor():
        raise ImageException('No valid image descripter')

    if reader.width != 16:
        raise ImageException('Image width incorrect')

    if reader.height != 16:
        raise ImageException('Image height incorrect')
    
    frames, header = read_gif_frames(reader)
    store(destination, frames, version, header)

    return 


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

    parser.add_argument('--version', '-v', type=int, help='frame file version', default=1)
    args = parser.parse_args()

    path = Path(args.image)
    image = create_from_gif(path, args.output or Path(path.parent), args.version)

    exit(0)
