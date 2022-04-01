import ast
import logging
import re
from dataclasses import dataclass
from typing import Callable, Optional

from fs import open_fs
from thefuzz import fuzz, process


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

    def __str__(self) -> str:
        """
        Define unique id as string.

        :returns: the string representation of the class ref.
        """
        return f"{self.module_path}.{self.class_name}"

    @staticmethod
    def from_string(string: str) -> "ClassRef":
        """
        Create a ClassRef object from a string.

        :params: the string to create the ClassRef from.

        :returns: the ClassRef object.
        """
        module_path, class_name = string.rsplit(".", 1)
        return ClassRef(module_path, class_name)


@dataclass
class ClassRefMatchObject:
    """A unique reference to a python class prepared for matching with other classes."""

    class_ref: ClassRef
    text: str


class MatchNotFoundError(Exception):
    """An exception raised when no match could be found."""


@dataclass
class ClassRefMatcher:
    """A class for matching class references."""

    query: ClassRef
    query_cleanup: Optional[Callable[[str], str]]
    choices: list[ClassRef]
    choice_cleanup: Optional[Callable[[str], str]]
    abbreviations: Optional[dict[str, str]]

    def match(self, mappings: Optional[dict[str, str]] = None) -> ClassRef:
        """
        Find best match for a query, giving choices. Optionally using mappings.

        :params mappings: A static dictionary of mappings.

        :returns: the match object.
        """
        mappings = mappings or {}
        for mapping_from, mapping_to in mappings.items():
            if self.query == ClassRef.from_string(mapping_from):
                logging.debug("Mapped to: %s", mapping_to)
                return ClassRef.from_string(mapping_to)

        _query = ClassRefMatchObject(
            class_ref=self.query,
            text=self._generate_text(
                class_ref_str=self.query_cleanup(str(self.query))
                if self.query_cleanup
                else str(self.query),
            ),
        )
        logging.debug("Query: %s", _query)
        _choices = [
            ClassRefMatchObject(
                class_ref=choice,
                text=self._generate_text(
                    class_ref_str=self.choice_cleanup(str(choice))
                    if self.choice_cleanup
                    else str(choice),
                ),
            )
            for choice in self.choices
        ]
        matches = process.extractBests(
            _query.text,
            [_choice.text for _choice in _choices],
            scorer=fuzz.token_set_ratio,
            score_cutoff=75,
        )
        logging.debug("Matches: %s", matches)
        if matches:
            matches.sort(
                key=lambda match: (match[1], len(match[0].split())),
                reverse=True,
            )
            logging.debug("Matches (sorted): %s", matches)
            choice = next(
                filter(lambda _choice: _choice.text == matches[0][0], _choices),
            )
            return choice.class_ref
        raise MatchNotFoundError("No match found!")

    def _generate_text(self, class_ref_str: str) -> str:
        if self.abbreviations:
            class_ref_str = self._replace_abbreviations(
                class_ref_str,
                abbreviations=self.abbreviations,
            )
        class_ref = ClassRef.from_string(class_ref_str)
        class_ref.class_name = " ".join(
            re.findall(r"[A-Z][^A-Z]*", class_ref.class_name),
        )
        return str(class_ref).replace(".", " ").replace("_", " ")

    def _replace_abbreviations(self, word: str, abbreviations: dict[str, str]) -> str:
        for k, v in abbreviations.items():
            word = word.replace(k, v).replace(
                k.lower(),
                "_".join(re.findall(r"[A-Z][^A-Z]*", v)).lower(),
            )
        return word


def retrieve_class_refs(directory: str) -> list[ClassRef]:
    """
    Retrieve class references from directory.

    :params directory: The directory from which to start parsing.

    :returns: a list of class references.
    """
    class_refs: list[ClassRef] = []

    fs = open_fs(directory)
    for path in fs.walk.files(filter=["*.py"], exclude=["__init__.py"]):
        with fs.open(path) as python_file:
            module_path = path.removeprefix("/").removesuffix(".py").replace("/", ".")

            for node in ast.walk(ast.parse(python_file.read())):
                if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                    class_refs.append(
                        ClassRef(
                            module_path=module_path,
                            class_name=node.name,
                        ),
                    )

    return class_refs
