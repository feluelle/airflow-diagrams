from airflow_diagrams.diagrams import to_var, wrap_str


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
