from airflow_diagrams.utils import load_abbreviations, load_mappings, to_var, wrap_str


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


def test_to_var():
    """Test converting to python variable"""
    var = to_var("foo-bar")
    assert "-" not in var and "." not in var
    assert var.startswith("_")


def test_wrap_str__indicator_number():
    """Test wrapping a string based on number"""
    assert wrap_str("foobarfoobar", "10") == "foobarfoob\\nar"


def test_wrap_str__indicator_separator():
    """Test wrapping a string based on separator"""
    assert wrap_str("foobarfoobar", "foo") == "\\nbar\\nbar"
