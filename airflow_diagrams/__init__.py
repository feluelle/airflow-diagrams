"""Top-level package for airflow-diagrams."""
from os import getcwd
from os.path import dirname, join, realpath

import toml

config = toml.load("pyproject.toml")

__app_name__ = config["tool"]["poetry"]["name"]
__version__ = config["tool"]["poetry"]["version"]
__location__ = realpath(join(getcwd(), dirname(__file__)))
