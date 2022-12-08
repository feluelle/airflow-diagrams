import json
import os

from airflow_diagrams import __location__
from airflow_diagrams.utils import load_abbreviations, load_mappings


def test_load_abbreviations(mocker):
    """Test loading abbreviations"""
    abbreviations = {"f": "foo"}
    mock_open = mocker.patch(
        "builtins.open",
        mocker.mock_open(read_data=json.dumps(abbreviations)),
    )
    assert load_abbreviations() == abbreviations
    mock_open.assert_called_once_with(os.path.join(__location__, "abbreviations.yml"))


def test_load_mappings(mocker):
    """Test loading mappings"""
    file_path = "mappings.yml"
    mappings = {"airflow.task.Foo": "diagrams.node.Bar"}
    mock_open = mocker.patch(
        "builtins.open",
        mocker.mock_open(read_data=json.dumps(mappings)),
    )
    assert load_mappings(file=file_path) == mappings
    mock_open.assert_called_once_with(file_path)
