import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import yaml
from blessed import Terminal

from airflow_diagrams import __location__


def load_abbreviations() -> dict:
    """
    Load abbreviations from a yaml file.

    :returns: a dict of abbreviation mapping.
    """
    with open(
        os.path.join(__location__, "abbreviations.yml"),
        "r",
    ) as abbreviations_yaml:
        return yaml.safe_load(abbreviations_yaml)


def load_mappings(file: Path) -> dict:
    """
    Load mappings from a yaml file.

    :params file: The file to load.
    :returns: a dict of Airflow task to diagram node mapping.
    """
    with open(
        file,
        "r",
    ) as mapping_yaml:
        return yaml.safe_load(mapping_yaml)


@contextmanager
def print_group(collapse: bool, seconds: float = 2) -> Generator:
    """
    Define a group that can be collapsed at the end.

    :params collapse: If set to True, group will be collapsed at the end.
    :params seconds: After how many seconds the group will be collapsed.
    """
    if collapse:
        term = Terminal()
        with term.location():
            start, _ = term.get_location()
            yield
            end, _ = term.get_location()
            time.sleep(seconds)
            print((term.move_up() + term.clear_eol) * (end - start))
    else:
        yield
