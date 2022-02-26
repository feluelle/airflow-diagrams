import pytest
from typer.testing import CliRunner

from airflow_diagrams import __app_name__, __version__, cli

runner = CliRunner()


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
                    module_path="module.path",
                    class_name="ClassName",
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
    assert (
        "ℹ️ Retrieved Airflow DAG test_dag.\n"
        "  ℹ️ Retrieved Airflow Task test_task (module.path.ClassName) with downstream tasks [].\n"
        "  🔮Found match programming.flowchart.Action.\n"
        "🪄 Generated diagrams file generated/test_dag_diagrams.py.\n"
        "\n"  # New line due to progress bar
        "Done. 🎉\n"
    ).replace("\n", "") == result.stdout.replace("\n", "")


def test_generate_with_verbose(mock_dag):
    """Test that logging level is DEBUG"""
    result = runner.invoke(
        cli.app,
        ["generate", "--output-path", "generated/", "--verbose"],
    )
    assert result.exit_code == 0
    assert result.stdout.startswith("💬 Running with verbose output..")
