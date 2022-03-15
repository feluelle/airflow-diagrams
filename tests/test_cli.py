import pytest
from typer.testing import CliRunner

from airflow_diagrams import __app_name__, __version__, cli

runner = CliRunner()


def strip_white_space(*strings) -> str:
    """
    Strip white spaces (including new line and tabs) from a string.

    :params strings: The strings to strip the white spaces from.

    :returns: the stripped string.
    """
    return "".join(strings).replace(" ", "").replace("\t", "").replace("\n", "")


@pytest.fixture
def mock_dag(airflow_api_tree):
    airflow_api_tree.dag_api.get_dags.return_value = dict(
        dags=[
            dict(
                dag_id="test_dag",
            ),
        ],
    )
    airflow_api_tree.dag_api.get_tasks.return_value = dict(
        tasks=[
            dict(
                class_ref=dict(
                    module_path="module.operators.path",
                    class_name="ClassNameOperator",
                ),
                task_id="test_task",
                downstream_task_ids=[],
            ),
        ],
    )


def test_version():
    """Test printing version"""
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" == result.stdout


def test_generate(mock_dag):
    """Test end-to-end"""
    result = runner.invoke(cli.app, ["generate", "--output-path", "generated/"])
    assert result.exit_code == 0
    assert strip_white_space(
        "ℹ️ Retrieving Airflow DAGs...",
        "  ℹ️ Retrieving Airflow Tasks for Airflow DAG test_dag...",
        "🪄 Processing Airflow DAG test_dag...",
        "  🪄 Processing Airflow Task test_task (module.operators.path.ClassNameOperator) with downstream tasks []...",
        "  🔮No match found! Falling back to programming.flowchart.Action.",
        "🎨Generated diagrams file generated/test_dag_diagrams.py.",
        "Done. 🎉",
    ) == strip_white_space(result.stdout)


def test_generate_with_progress(mock_dag):
    """Test end-to-end"""
    result = runner.invoke(
        cli.app,
        ["generate", "--output-path", "generated/", "--progress"],
    )
    assert result.exit_code == 0
    assert strip_white_space(
        "ℹ️ Retrieving Airflow DAGs...",
        "  ℹ️ Retrieving Airflow Tasks for Airflow DAG test_dag...",
        "🪄 Processing Airflow DAG test_dag...",
        "  🪄 Processing Airflow Task test_task (module.operators.path.ClassNameOperator) with downstream tasks []...",
        "  🔮No match found! Falling back to programming.flowchart.Action.",
        "🎨Generated diagrams file generated/test_dag_diagrams.py.",
        "Done. 🎉",
    ) == strip_white_space(result.stdout)


def test_generate_with_verbose(mock_dag):
    """Test that logging level is DEBUG"""
    result = runner.invoke(
        cli.app,
        ["generate", "--output-path", "generated/", "--verbose"],
    )
    assert result.exit_code == 0
    assert result.stdout.startswith("💬 Running with verbose output...")


@pytest.mark.order(after="test_download")
def test_generate_from_file(mock_dag):
    """Test generate from Airflow info file"""
    result = runner.invoke(
        cli.app,
        ["generate", "--output-path", "generated/", "-f", "generated/airflow_dags.yml"],
    )
    assert result.exit_code == 0
    assert strip_white_space(
        "📝Loading Airflow information from file...",
        "🪄 Processing Airflow DAG test_dag...",
        "  🪄 Processing Airflow Task test_task (module.operators.path.ClassNameOperator) with downstream tasks []...",
        "  🔮No match found! Falling back to programming.flowchart.Action.",
        "🎨Generated diagrams file generated/test_dag_diagrams.py.",
        "Done. 🎉",
    ) == strip_white_space(result.stdout)


def test_download(mock_dag):
    """Test downloading Airflow information"""
    result = runner.invoke(cli.app, ["download", "generated/airflow_dags.yml"])
    assert result.exit_code == 0
    assert strip_white_space(
        "ℹ️ Retrieving Airflow DAGs...",
        "  ℹ️ Retrieving Airflow Tasks for Airflow DAG test_dag...",
        "📝Dumping to file...",
        "Done. 🎉",
    ) == strip_white_space(result.stdout)
