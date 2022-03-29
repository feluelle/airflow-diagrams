import ast
import re

import pytest

from airflow_diagrams.class_ref import ClassRef, ClassRefMatcher, retrieve_class_refs


@pytest.fixture
def class_ref():
    return ClassRef(
        module_path="module.operators.path",
        class_name="ClassNameOperator",
    )


@pytest.fixture
def class_ref_matcher(class_ref):
    return ClassRefMatcher(
        query=class_ref,
        query_cleanup=lambda query_str: (
            query_str.removeprefix("airflow.providers.")
            .replace(".operators.", ".")
            .replace(".sensors.", ".")
            .replace(".transfers.", ".")
            .removesuffix("Operator")
            .removesuffix("Sensor")
        ),
        choices=[class_ref],
        choice_cleanup=lambda choice_str: (
            ".".join(re.findall(r"(.*)\.(?:.*)\.(.*)", choice_str)[0])
        ),
        abbreviations=dict(),
    )


def test_class_ref_str_and_from_string(class_ref):
    """Test converting a ClassRef to str & creating a ClassRef from a string"""
    assert ClassRef.from_string(str(class_ref)) == class_ref


def test_class_ref_matcher_match(class_ref_matcher):
    """Test matching"""
    assert class_ref_matcher.match() == class_ref_matcher.choices[0]


def test_class_ref_matcher_match_with_mappings(class_ref_matcher):
    """Test matching with mappings"""
    query_str = str(class_ref_matcher.query)
    mappings = {query_str: "test.custom.module.operators.path.ClassNameOperator"}
    assert class_ref_matcher.match(mappings=mappings) == ClassRef.from_string(
        mappings[query_str],
    )


def test_retrieve_class_refs(mocker):
    """Test retrieving class refs from directory"""
    mocker.patch(
        "os.walk",
        return_value=[
            ("/module", (), ("path.py",)),
        ],
    )
    mocker.patch("builtins.open")
    mocker.patch(
        "ast.parse",
        return_value=ast.Module(
            body=[
                ast.ClassDef(name="ClassName", lineno=1),
            ],
        ),
    )

    assert retrieve_class_refs(directory="/module/") == [
        ClassRef(module_path="path", class_name="ClassName"),
    ]
