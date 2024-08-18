# frame simulator
Frame is a small led-matrix controller build for raspberry pi. This simulator uses Pygame to simulate without an actual display. Frame uses a custom file format, with the colors for every pixel. I used a small converter script to create `.frame` files from gifs.  I wouldn't have gotten far without [pygif](https://github.com/robert-ancell/pygif) of Robert Ancell and the explanation of [Christophe Tronche](https://tronche.com/computer-graphics/gif/gif89a.html#image-descriptor).

The [main branch](https://github.com/martijncasteel/frame/tree/main) holds the code for the program to be ran on a raspberry pi!

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. A step by step series of examples that tell you how to get a development env running

```bash
# setting up environment
python3 -m venv env
source env/bin/activate

# install pygame once
pip install pygame

# run the program
python -m frame-simulator /directory/to/frame-files

# reload available files from image folder
ps aux | grep -i "python -m frame-simulator"
kill -USR1 $pid
```

## Create `.frame` files
```bash
# setting up environment
python3 -m venv env
source env/bin/activate

# install python library
pip install pygif

# run parser
python sample/parse.py sample/bird.gif [--output FILE/DIRECTORY]

# try it out 
python -m frame sample/
```

## Contributing
Please read [the contributing guidelines](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us. We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags](https://github.com/martijncasteel/frame-simulator/tags) on this repository. 

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

