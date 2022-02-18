from unittest.mock import PropertyMock

import pytest
from blessed import Terminal
from typer.testing import CliRunner

from airflow_diagrams import __app_name__, __version__, cli

runner = CliRunner()


@pytest.fixture
def mock_term(mocker):
    mock_get_location = mocker.patch.object(
        Terminal,
        "get_location",
        side_effect=[(0, 0), (3, 0)],
    )
    mock_move_up = mocker.patch.object(Terminal, "move_up", return_value="\033[A")
    mock_clear_eol = mocker.patch.object(
        Terminal,
        "clear_eol",
        new_callable=PropertyMock,
        create=True,
        return_value="\033[K",
    )
    yield
    assert mock_get_location.call_count == 2
    assert mock_move_up.call_count == 1
    assert mock_clear_eol.call_count == 1


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


def test_generate(mock_dag, mock_term, mocker):
    """Test end-to-end"""
    mocker.patch("time.sleep", return_value=None)
    result = runner.invoke(cli.app, ["generate", "--output-path", "generated/"])
    assert result.exit_code == 0
    assert (
        "ℹ️ Retrieved Airflow DAG test_dag.\n"
        "  ℹ️ Retrieved Airflow Task test_task (module.path.ClassName) with downstream tasks [].\n"
        "  🔮Found match programming.flowchart.Action.\n"
        "\x1b[A\x1b[K\x1b[A\x1b[K\x1b[A\x1b[K\n"
        "🪄 Generated diagrams file generated/test_dag_diagrams.py.\n"
        "Done. 🎉\n"
    ) == result.stdout


def test_generate_with_verbose(mock_dag):
    """Test that logging level is DEBUG"""
    result = runner.invoke(
        cli.app,
        ["generate", "--output-path", "generated/", "--verbose"],
    )
    assert result.exit_code == 0
    assert result.stdout.startswith("💬 Running with verbose output..")
    assert (
        "ℹ️ Retrieved Airflow DAG test_dag.\n"
        "  ℹ️ Retrieved Airflow Task test_task (module.path.ClassName) with downstream tasks [].\n"
        "  🔮Found match programming.flowchart.Action.\n"
        "🪄 Generated diagrams file generated/test_dag_diagrams.py.\n"
        "Done. 🎉\n"
    ) in result.stdout
