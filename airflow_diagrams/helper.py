import ast
import json
import logging
import os
from dataclasses import dataclass
from os.path import dirname
from re import findall
from typing import Generator, Optional

import diagrams
import requests
import yaml
from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader
from jinja2.runtime import StrictUndefined
from requests.auth import HTTPBasicAuth
from thefuzz import fuzz, process

from airflow_diagrams import __location__

MATCHING_PERCENTAGE_MIN: int = 75


@dataclass
class ClassRef:
    """A unique reference to a python class."""

    module_path: str
    class_name: str

    def __hash__(self) -> int:
        """
        Build a hash based on all attributes.

        :returns: a hash of all attributes.
        """
        return hash(self.module_path) ^ hash(self.class_name)


@dataclass
class ClassRefMatchObject:
    """A unique reference to a python class prepared for matching with other classes."""

    class_ref: ClassRef
    text: str


@dataclass
class ClassRefMatcher:
    """A class for matching class references."""

    query: ClassRef
    choices: list[ClassRef]
    query_options: dict
    choices_options: dict

    def match(self) -> ClassRef:
        """
        Find best match for a query, giving choices.

        :returns: the match object.
        """
        _query = ClassRefMatchObject(
            class_ref=self.query,
            text=self._generate_text(class_ref=self.query, **self.query_options),
        )
        logging.debug("Query: %s", _query)
        _choices = [
            ClassRefMatchObject(
                class_ref=choice,
                text=self._generate_text(class_ref=choice, **self.choices_options),
            )
            for choice in self.choices
        ]
        result = process.extractOne(
            _query.text,
            [_choice.text for _choice in _choices],
            scorer=fuzz.token_set_ratio,
        )
        logging.debug("Result: %s", result)
        return next(
            filter(
                lambda _choice: _choice.text == result[0]
                and result[1] >= MATCHING_PERCENTAGE_MIN,
                _choices,
            ),
            self._get_fallback_class_ref_match_object(),
        ).class_ref

    def _get_fallback_class_ref_match_object(self) -> ClassRefMatchObject:
        class_ref_blank = ClassRef(
            module_path="generic.blank",
            class_name="Blank",
        )
        return ClassRefMatchObject(
            class_ref=class_ref_blank,
            text=self._generate_text(class_ref=class_ref_blank, **self.choices_options),
        )

    def _generate_text(
        self,
        class_ref: ClassRef,
        removesuffixes: Optional[list[str]],
        replaceabbreviations: Optional[dict],
    ) -> str:
        class_name = class_ref.class_name
        if removesuffixes:
            class_name = self._remove_suffixes(
                class_name,
                suffixes=removesuffixes,
            )
        if replaceabbreviations:
            class_name = self._replace_abbreviations(
                class_name,
                abbreviations=replaceabbreviations,
            )
        class_name = " ".join(findall("[A-Z][^A-Z]*", class_name))

        module_path = class_ref.module_path
        if replaceabbreviations:
            module_path = self._replace_abbreviations(
                module_path,
                abbreviations=replaceabbreviations,
            )
        module_path = module_path.replace(".", " ").replace("_", " ")

        return f"{module_path} {class_name}"

    def _remove_suffixes(self, word: str, suffixes: list[str]) -> str:
        for suffix in suffixes:
            word = word.removesuffix(suffix)
        return word

    def _replace_abbreviations(self, word: str, abbreviations: dict) -> str:
        for k, v in abbreviations.items():
            word = word.replace(k, v)
        return word


class AirflowClient:
    """A client to interact with Airflow REST-API."""

    # TODO: Use apache airflow-client-python when issue is fixed
    #   See https://github.com/apache/airflow-client-python/issues/20 for more information.

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
    ) -> None:
        self.host = host
        self.auth = HTTPBasicAuth(username, password)

    def get_dags(
        self,
    ) -> Generator[str, None, None]:
        """
        Retrieve all dags.

        :returns: a generator of dag objects.
        """
        response = requests.get(
            url=f"{self.host}/dags",
            auth=self.auth,
        )
        return (dag["dag_id"] for dag in json.loads(response.text)["dags"])

    def get_tasks(
        self,
        dag_id: str,
    ) -> Generator[dict, None, None]:
        """
        Retrieve tasks for a given dag id.

        :param dag_id: The id of the dag to retrieve tasks for.

        :returns: a generator of task objects.
        """
        response = requests.get(
            url=f"{self.host}/dags/{dag_id}/tasks",
            auth=self.auth,
        )
        return (task for task in json.loads(response.text)["tasks"])


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
