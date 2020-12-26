<h1 align="center">Pycee</h1>

<p align="center">
  <a href="https://github.com/marceloFA/pycee2/actions"><img alt="pycee2 status" src="https://github.com/marceloFA/pycee2/workflows/Test%20pycee2/badge.svg?branch=master"></a>
  <a href="https://codecov.io/gh/marceloFA/pycee2"><img alt="pycee2 coverage" src="https://codecov.io/gh/marceloFA/pycee2/branch/master/graph/badge.svg?token=MQI078A12M"></a>
  <a href="https://opensource.org/licenses/MIT"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
  <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

Pycee is a tool to provide possible solutions for errors in python code.
Solutions are from Stackoverflow questions that may be related to the code error.
This is a reimplementation of [Emillie Thiselton's Pycee](https://github.com/EmillieT/Pycee).

### Live demo
Trying out pycee2 without installing is possible through the [web application](https://pycee.herokuapp.com).
It uses [PythonBuddy](https://github.com/marceloFA/PythonBuddy) as a python editor for the web with linting included.

### :gear: Installation

```console
pip3 install pycee2
```

### :computer: Using Pycee2

After installation, all you have to do is to call ``pycee`` passing the name of the file that contains the error.

```console
 pycee file_with_error.py
 ```

Here's an example:
Suppose ``script.py`` contains the following code:
```python
# Brazil world cup titles by year
world_cup_titles = [1958,1962,1970,1994,2002]
# print year of the 5th title
print(world_cup_titles[5])
```
executing this script will result in an error like this:
```console
Traceback (most recent call last):
  File "example_code.py", line 4, in <module>
    print(world_cup_titles[5])
IndexError: list index out of range
```
Then you can use pycee to provide a possible answer for the error, like so:
```console
pycee script.py
```
Which, finally, will output some answers from StackOverflow that are possibly related to your error:
```console
Solution 1:
Generally, it means that you are providing an index for which a list element
does not exist.

E.g, if your list was [1, 3, 5, 7], and you asked for the element at index
10, you would be well out of bounds and receive an error, as only elements 0
through 3 exist.

...
(rest of the output with two more answers omitted from this example)
```

### :construction_worker: Setup script for contributors

```console

# clone the repository your development environment
git clone https://github.com/marceloFA/pycee2.git

# cd into the project directory
cd pycee2/

# create a virtual environment to install packages isolatedly
python3 -m venv venv # if you use venv
virtualenv venv      # else if you use virtualenv

# activate the virtual env
source venv/bin/activate

# install packages required to run pycee
pip3 install -r requirements.txt requirements-dev.txt

#  using pycee in development mode, from the project root
python3 usage.py example_code.py

# running tests, from the project root
pytest
```

### :building_construction: Maintainers

| [![Leonardo Furtado](https://github.com/LeonardoFurtado.png?size=100)](https://twitter.com/furtleo) | [![Marcelo Almeida](https://github.com/marceloFA.png?size=100)](https://github.com/marceloFA) |
| :-----------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------: |
|          [Leonardo Furtado](https://github.com/LeonardoFurtado)                                           |          [Marcelo Almeida](https://github.com/marceloFA)      
