import struct

HEADER_SIZE = 16
HEADER_COLOR_TABLE = 2

class Image():

    def __init__(self, file):
        self.file = file

        signature, self.version, self.width, self.height, self.frame_count, \
        self.loop_count = struct.unpack('!7sB 4x BBBB', self.file.read(HEADER_SIZE))

        if signature != b'\x87\x46\x52\x41\x4d\x45\x0A':
            raise ImageException(f'unknown file format: {file.name}')


        if self.version == 1:
            return

        # read length of color_table and padding, and fill color_table
        self.color_table_size, self.color_table_padding = struct.unpack('!BB', self.file.read(HEADER_COLOR_TABLE))
        self.color_table = []
        
        for _ in range(self.color_table_size):
            self.color_table.append(struct.unpack('!BBB', self.file.read(3)))

        self.file.seek(self.color_table_padding, 1)

    def display(self, controller):
        for _ in range(0, self.loop_count): 
            for frame in range(self.frame_count):

                delay = self.__read_frame(controller, frame)

                controller.sleep(next_showing = delay/1000)
                controller.draw()
            
            self.__rewind()


    def __read_frame(self, controller, index) -> int:

        # short for delay and 3 bytes per color
        if self.version == 1: 
            delay = struct.unpack('!H', self.file.read(2))[0]
            frame = self.file.read(self.width * self.height * 3)
                        
            for y in range(self.height):
                for x in range(self.width):
                    index = (x + y * self.width) * 3
                    controller[(x,y)] = struct.unpack('!BBB', frame[index:index+3])

            return delay

        # short for delay, byte for pointer to color table
        if self.version == 2:
            delay = struct.unpack('!H', self.file.read(2))[0]
            
            for y in range(self.height):
                for x in range(self.width):
                    color_table_index = struct.unpack('!B', self.file.read(1))[0]
                    controller[(x,y)] = self.color_table[color_table_index]

            return delay
        raise ImageException('unsupported file version')


    def __rewind(self):
        if self.version == 1:
            self.file.seek(HEADER_SIZE)

        elif self.version == 2:
            self.file.seek(HEADER_SIZE + HEADER_COLOR_TABLE + self.color_table_size * 3 + self.color_table_padding)

        else:
            raise ImageException('unsupported file version')


class ImageException(Exception):
    """Raised when file is not being parsed"""