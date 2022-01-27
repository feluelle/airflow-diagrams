import os
from hashlib import md5
from os.path import dirname
from pathlib import Path
from textwrap import wrap

import yaml
from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader
from jinja2.runtime import StrictUndefined

from airflow_diagrams import __location__


def render_jinja(template_file: str, context: dict, output_file: str) -> None:
    """
    Render the context, given a template file, to a file.

    :param template_file: The file containing the template to render.
    :param context: The context to pass to the template_file.
    :param output_file: The file to output the rendered version.
    """
    (
        Environment(
            loader=FileSystemLoader(dirname(__file__)),
            undefined=StrictUndefined,
            autoescape=True,
        )
        .get_template(template_file)
        .stream(**context)
        .dump(output_file)
    )


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


def to_var(string: str) -> str:
    """
    Convert a string to a valid python variable name.

    :params string: The string to convert.
    :returns: a valid python variable name.
    """
    return f"_{md5(string.encode()).hexdigest()}"  # nosec


def wrap_str(string: str, indicator: str) -> str:
    """
    Wrap a string with newline chars based on indicator.

    :params string: The string to wrap.
    :params indicator: Specify either a number for width or a separator to indicate when to wrap.
    :returns: the wrapped string.
    """
    if indicator.isdigit():
        return "\\n".join(wrap(string, int(indicator), break_on_hyphens=False))
    return "\\n".join(string.split(indicator))
