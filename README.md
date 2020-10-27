# Pycee 2 (WIP)
This is a refactored version of [pycee])(https://github.com/EmillieT/Pycee).
Pycee 2 is a tool that provides enhanced error messages for Python code.


# Installation
```console
pip3 install -r requirements.txt
```
Creating a virtual environment is optional but recommended.

# Testing
Two simple steps are required for testing pycee2. You have to install pycee2 as a package inside your virtual env and execute pytest. From the project root, it's as simple as this:
```console
pip3 install -e .
pytest
```

# Usage
For now, to use Pycee get some traceback of an error you have and put it in ``example_error_message.txt``
and the code that generates the error in ``example_code.py``.
Then on the command line, inside the project root dir aimply execute ``python3 pycee/pycee.py``.
