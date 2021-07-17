"""
Simple command line tool to parse images to the frame format
"""

import argparse
from pathlib import Path
from common.images import Image


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Frame parser')
    parser.add_argument('image', help='image to parse')
    parser.add_argument('--output', '-o', help='output directory')

    parser.add_argument('--version', '-v', type=int, help='frame file version', default=1)
    args = parser.parse_args()

    path = Path(args.image)
    image = Image.create_from_gif(path, args.output or Path(path.parent), args.version)

    exit(0)
