import logging
from dataclasses import dataclass
from re import findall
from typing import Optional

from thefuzz import fuzz, process

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


@dataclass
class ClassRefMatcher:
    """A class for matching class references."""

    query: ClassRef
    choices: list[ClassRef]
    query_options: dict
    choices_options: dict

    def match(self, mappings: Optional[dict] = None) -> ClassRef:
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
