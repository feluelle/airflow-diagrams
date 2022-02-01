from airflow_diagrams.utils import load_abbreviations, load_mappings


def test_load_abbreviations(mocker):
    """Test loading abbreviations"""
    mocker.patch("builtins.open", mocker.mock_open(read_data='{"f":"foo"}'))
    assert load_abbreviations() == dict(f="foo")


def test_load_mappings(mocker):
    """Test loading mappings"""
    file_path = "mappings.yml"
    mock_open = mocker.patch(
        "builtins.open",
        mocker.mock_open(read_data='{"airflow.task.Foo":"diagrams.node.Bar"}'),
    )
    assert load_mappings(file=file_path) == {"airflow.task.Foo": "diagrams.node.Bar"}
    mock_open.assert_called_once_with(file_path, "r")
