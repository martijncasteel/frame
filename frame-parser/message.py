import sys
import struct

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

