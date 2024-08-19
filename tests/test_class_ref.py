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
def class_ref_mapped():
    return ClassRef(
        module_path="test.custom.module.operators.path",
        class_name="ClassNameOperator",
    )


@pytest.fixture
def class_ref_matcher(class_ref):
    return ClassRefMatcher(
        choices=[class_ref],
        choice_cleanup=lambda choice_str: (
            ".".join(re.findall(r"(.*)\.(?:.*)\.(.*)", choice_str)[0])
        ),
    )


@pytest.fixture
def class_ref_matcher_with_mappings(class_ref, class_ref_mapped):
    return ClassRefMatcher(
        choices=[class_ref],
        choice_cleanup=lambda choice_str: (
            ".".join(re.findall(r"(.*)\.(?:.*)\.(.*)", choice_str)[0])
        ),
        mappings={str(class_ref): str(class_ref_mapped)},
    )


@pytest.fixture
def match_kwargs(class_ref):
    return dict(
        query=class_ref,
        query_cleanup=lambda query_str: (
            query_str.removeprefix("airflow.providers.")
            .replace(".operators.", ".")
            .replace(".sensors.", ".")
            .replace(".transfers.", ".")
            .removesuffix("Operator")
            .removesuffix("Sensor")
        ),
    )


def test_class_ref_str_and_from_string(class_ref):
    """Test converting a ClassRef to str & creating a ClassRef from a string"""
    assert ClassRef.from_string(str(class_ref)) == class_ref


def test_class_ref_matcher_match(class_ref_matcher, class_ref, match_kwargs):
    """Test matching"""
    assert class_ref_matcher.match(**match_kwargs) == class_ref


def test_class_ref_matcher_match_with_mappings(
    class_ref_matcher_with_mappings,
    class_ref,
    class_ref_mapped,
    match_kwargs,
):
    """Test matching with mappings"""
    assert class_ref_matcher_with_mappings.match(**match_kwargs) == class_ref_mapped


def test_retrieve_class_refs(mocker):
    """Test retrieving class refs from directory"""
    fs = mocker.patch("airflow_diagrams.class_ref.open_fs")
    fs.return_value.walk.files.return_value = ["/module/path.py"]
    mocker.patch(
        "ast.parse",
        return_value=ast.Module(
            body=[
                ast.ClassDef(name="ClassName", lineno=1),
            ],
        ),
    )

    assert retrieve_class_refs(directory="/module/") == [
        ClassRef(module_path=".module.path", class_name="ClassName"),
    ]
