"""
Simple command line tool to parse images to the frame format
"""
import os
import argparse

from pathlib import Path
from helpers.image import Image, ImageException


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
