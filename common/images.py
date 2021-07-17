import math
import struct
import gif

from pathlib import Path

HEADER_SIZE = 16

class Image():

    # 7B      application signature       87 46 52 41 4d 45 0D
    # 1B      version  
    # -------------------------------------------------------
    # 4B      padding   
    # 1B      width             
    # 1B      height
    # 1B      number of frames  
    # 1B      number of repeats of all frames (loops)
    # -------------------------------------------------------
    # 1B      delay in ms
    # 3B      color     width*height*3 per frame
    # -------------------------------------------------------

    # def __init__(self, file):
    #     self.file = file
 
    @classmethod
    def load(self, file):
        """Load file with frame format"""
        image = Image()
        image.file = file

        signature, image.version, image.width, image.height, image.frame_count, \
        image.loop_count = struct.unpack('!7sB 4x BBBB', image.file.read(HEADER_SIZE))

        if signature != b'\x87\x46\x52\x41\x4d\x45\x0A':
            raise ImageException(f'unknown file format: {file.name}')

        return image


    def display(self, controller):

        def read_frame(controller, index):

            # 1 bytes for delay and 3 bytes per color
            if self.version == 1: 
                delay = struct.unpack('!H', self.file.read(2))[0]
                frame = self.file.read(self.width * self.height * 3)
                            
                for y in range(self.height):
                    for x in range(self.width):
                        index = (x + y * self.width) * 3
                        controller[(x,y)] = struct.unpack('!BBB', frame[index:index+3])

                return delay

            else:
                raise ImageException('unsupported file version')


        def rewind():
            if self.version == 1:
                self.file.seek(HEADER_SIZE)


        # loop `loop_count` times 
        for _ in range(0, self.loop_count): 
            for frame in range(0, self.frame_count):

                delay = read_frame(controller, frame)

                controller.sleep(next_showing = delay/1000)
                controller.draw()
            
            rewind()


    @classmethod
    def create_from_gif(self, path, destination, version):
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
                            pixels[Image.transpose(index, block)] = block.color_table[pixel]
                        elif len(reader.color_table) > 0:
                            pixels[Image.transpose(index, block)] = reader.color_table[pixel]
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


    @staticmethod
    def transpose(index, image):
        """
        Use index and frame dimension to calculate index based on a (16,16) canvas
        Not all frames start at (0,0)
        """
        row = math.floor(index / image.width)
        return (index % image.width + image.left) + (row + image.top) * 16

class ImageException(Exception):
    """Raised when file is not being parsed"""