import struct

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


    def __init__(self, file):
        self.file = file

        signature, self.version, self.width, self.height, self.frame_count, \
        self.loop_count = struct.unpack('!7sB 4x BBBB', self.file.read(HEADER_SIZE))

        if signature != b'\x87\x46\x52\x41\x4d\x45\x0A':
            raise ImageException(f'unknown file format: {file.name}')


    def display(self, controller):
        for _ in range(0, self.loop_count): 
            for frame in range(0, self.frame_count):

                delay = self.__read_frame(controller, frame)

                controller.sleep(next_showing = delay/1000)
                controller.draw()
            
            self.__rewind()


    def __read_frame(self, controller, index):

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


    def __rewind(self):
        if self.version == 1:
            self.file.seek(HEADER_SIZE)

class ImageException(Exception):
    """Raised when file is not being parsed"""