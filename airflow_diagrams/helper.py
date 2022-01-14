import ast
import os
from os.path import dirname

import diagrams
import yaml
from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader
from jinja2.runtime import StrictUndefined

from airflow_diagrams import __location__
from airflow_diagrams.class_ref import ClassRef


def get_diagrams_class_refs() -> list[ClassRef]:
    """
    Get class references of the diagram module.

    :returns: a list of class references.
    """
    class_refs: list[ClassRef] = []
    directory = f"{os.path.dirname(diagrams.__file__)}/"

    for root, _, files in os.walk(directory):
        for file in files:
            if not file.endswith(".py") or file == "__init__.py":
                continue

            file_absolute_path = os.path.join(root, file)
            module_path = (
                file_absolute_path.removeprefix(
                    directory,
                )
                .removesuffix(".py")
                .replace("/", ".")
            )

            with open(file_absolute_path) as _file:
                _node = ast.parse(_file.read())

            for node in ast.walk(_node):
                if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                    class_refs.append(
                        ClassRef(
                            module_path=module_path,
                            class_name=node.name,
                        ),
                    )
    return class_refs


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


def load_mappings(file: str) -> dict:
    """
    Load mappings from a yaml file.

    :returns: a dict of Airflow task to diagram node mapping.
    """
    with open(
        file,
        "r",
    ) as mapping_yaml:
        return yaml.safe_load(mapping_yaml)
