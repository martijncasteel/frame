# Frame
Frame is a small led-matrix controller build for raspberry pi zero. Frame uses a custom file format, with colors for every pixel. I used a small converter script to create `.frame` files from gifs. I wouldn't have gotten far without [pygif](https://github.com/robert-ancell/pygif) of Robert Ancell and the explanation of [Christophe Tronche](https://tronche.com/computer-graphics/gif/gif89a.html#image-descriptor).


## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. A step by step series of examples that tell you how to get a development env running.

Start by checking out the [simulator](https://github.com/martijncasteel/frame/tree/simulator) branch!


## Create frame files
I thought it would be fun to create a own file format and it is but maybe not so convenient. Creating files can be done by converting gifs using the following command.

```bash
# setting up environment
python3 -m venv env
source env/bin/activate

# install dependencies
pip install pygif

python parse.py /path/to/file.gif
```


## Run the program on a Raspberry PI
The goal is to run this code on a raspberry pi with a 16 by 16 rgb led grid. To be able to do so we need some additional steps

```bash
# setting up environment
python3 -m venv env
source env/bin/activate

# install dependencies
pip install -r requirements.txt

# run the program with frame.service or use
python -m frame /directory/to/frame-files

# install service file
ln -s /var/local/frame/frame.service frame.service
```


## Contributing
Please read [the contributing guidelines](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us. We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags](https://github.com/martijncasteel/frame/tags) on this repository. 


## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

