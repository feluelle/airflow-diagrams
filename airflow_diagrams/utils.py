import logging
import os
from pathlib import Path

import yaml

from airflow_diagrams import __experimental__, __location__


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


def experimental(func):
    """Decorate experimental features."""

    def wrapper(*args, **kwargs):
        if __experimental__:
            logging.debug("Calling experimental feature: %s", func.__name__)
            func(*args, **kwargs)

    return wrapper
