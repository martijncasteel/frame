"""
Simple command line tool to parse images to the frame format
"""
import os
import math
import struct
import argparse
import gif

from pathlib import Path

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Frame parser')
    parser.add_argument('image', help='image to parse')
    parser.add_argument('--output', '-o', help='output directory')
    args = parser.parse_args()

    file = Path(args.image)
    frames = []

    # open the file and feed to parser
    image = open(file, 'rb') 
    reader = gif.Reader()
    reader.feed(image.read())
    loop_count = 1

    if not reader.has_screen_descriptor():
        raise TypeError('No valid image descripter')

    # for now only support 16 by 16 images
    if self.reader.width != 16:
        raise TypeError('Image width unsupported')

    if self.reader.height != 16:
        raise TypeError('Image height unsupported')

    # initialize background
    pixels = [reader.color_table[reader.background_color]] * (16*16)
    transparent_color = None
    delay = 0.01

    for block in reader.blocks:

        # read repeat count only once
        if isinstance(block, (gif.AnimationExtension, gif.NetscapeExtension)):
            if block.loop_count is not None:
                loop_count = block.loop_count

        # read delay before reading image
        elif isinstance(block, gif.GraphicControlExtension):
            delay = block.delay_time * 10

            if block.has_transparent or block.transparent_color != 0:
                transparent_color = block.transparent_color

        elif isinstance(block, gif.Image):
            frame = struct.pack('!H', int(delay))

            for index, pixel in enumerate(block.get_pixels()):

                if pixel == transparent_color:
                    continue
        
                pos = (index % block.width + block.left) + (math.floor(index / block.width) + block.top) * 16

                if len(block.color_table) > 0:
                    pixels[pos] = block.color_table[pixel]
                elif len(reader.color_table) > 0:
                    pixels[pos] = reader.color_table[pixel]

                else:
                    raise TypeError('color_table is incomplete')

            for color in pixels:
                frame += struct.pack('BBB', *color)
            
            frames.append(frame)

    
    # open destination file 
    destination = Path(args.output) if args.output else Path(file.parent)
    if not destination.is_dir():
        destination = Path(destination.parent) / f'{destination.stem}.frame'
    else:
        destination = destination / f'{file.stem}.frame'

    with open(destination, 'wb') as f:
        f.write(struct.pack('!7sB', b'\x87\x46\x52\x41\x4d\x45\x0A', 1))
        f.write(struct.pack('!4x BBBB', reader.width, reader.height, len(frames), loop_count))

        for frame in frames:
            f.write(frame)

    print(f'wrote {destination}')
    exit(0)
