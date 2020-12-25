# Pycee

Pycee is a tool to provide possible solutions for errors in python code. 
Solutions are from Stackoverflow questions that may be related to the code error.
This is a reimplementation of [Emillie Thiselton's Pycee](https://github.com/EmillieT/Pycee).  

### :gear: Installation

```console
pip3 install pycee
```

### :computer: Using Pycee2

After installed, all you have to do is to call ``pycee`` passing the name of the file that contains the error.

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
Then you can use pycee to provide an possible answer for the error, linke so:
```console
pycee script.py
```
Which, finally, will output some answers form stackoverflow that are possibily related to your error:
```console
Solution 1:
Generally it means that you are providing an index for which a list element
does not exist.

E.g, if your list was [1, 3, 5, 7], and you asked for the element at index
10, you would be well out of bounds and receive an error, as only elements 0
through 3 exist.

... 
(rest of the output with two more answers omitted from this example)
```

### :gear: Installation (for contributors)

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
