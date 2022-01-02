"""Top-level package for airflow-diagrams."""
from os import getcwd
from os.path import dirname, join, realpath

__app_name__ = "airflow-diagrams"
__version__ = "1.0.0.dev0"
__location__ = realpath(join(getcwd(), dirname(__file__)))
