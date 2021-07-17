"""
Simple simulator displaying received image on a 16 by 16 pygame 
window. Listening to port and display on new receive.
"""
import os
import signal
import argparse

from .controller import Controller

def handler(signum, _):
    """ signal handler """

    if(signum == signal.SIGUSR1):
        if controller:
            controller.reload(verbose=True)
        return

    print(f' interupt has been caught ({signum}), shutting down...')

    if controller:
        controller.shutdown()

    exit(0)

if __name__ == '__main__':

    signal.signal(signal.SIGINT, handler) 
    signal.signal(signal.SIGUSR1, handler)


    parser = argparse.ArgumentParser(description='Frame simulator')
    parser.add_argument('directory', help='image directory for binaries')
    args = parser.parse_args()

    controller = Controller(args.directory)
    while controller.running:
        # loop through all files
        controller.run()

        # re-populate the files list
        controller.reload()

    exit(0)
