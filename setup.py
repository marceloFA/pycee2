""" This file defines some information needed to punlish pycee2 at the package index (pip).
part of this code was authored by @navdeep-G and source can b found at:
https://github.com/navdeep-G/setup.py"""
import pathlib
import os
import sys
from shutil import rmtree
from setuptools import setup, find_packages, Command

NAME = "pycee2"
VERSION = "0.1"
PYTHON_REQUIRES = ">=3.7.0"
DESCRIPTION = "Enhanced error messages from Stackoverflow"
PACKAGE_URL = "https://github.com/marcelofa/pycee2"
AUTHOR = "Marcelo Freitas"
AUTHOR_EMAIL = "jmfda00@gmail.com"
MAINTAINER = "Leonardo Furtado"
MAINTAINER_EMAIL = "srleonardofurtado@gmail.com"
root_dir = pathlib.Path(__file__).parent

# get required packages from requirements.txt
try:
    with open("requirements.txt", "r") as f1:
        requirements = f1.readlines()
except FileNotFoundError:
    raise ("could not find requirements.txt")
required = [r.strip() for r in requirements]

# get README.md content
try:
    with open("README.md", "r") as f2:
        long_description = f2.read()
except FileNotFoundError:
    long_description = DESCRIPTION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(root_dir, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system(f"{sys.executable} setup.py sdist bdist_wheel --universal")

        self.status(f"Uploading {NAME} v{VERSION} to PyPI via Twine…")
        os.system("twine upload dist/*")

        self.status("Pushing git tags…")
        os.system(f"git tag v{VERSION}")
        os.system("git push --tags")

        sys.exit()


setup(
    name=NAME,
    version=VERSION,
    python_requires=PYTHON_REQUIRES,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=PACKAGE_URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=MAINTAINER,
    maintainer_email=MAINTAINER_EMAIL,
    packages=find_packages(exclude=("tests",)),
    # py_modules=["pycee"],
    install_requires=required,
    scripts=["usage.py"],
    entry_points={"console_scripts": ["pycee=usage:main"]},
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    cmdclass={
        "upload": UploadCommand,
    },
)
