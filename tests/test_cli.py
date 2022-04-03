import pytest
from typer.testing import CliRunner

from airflow_diagrams import __app_name__, __experimental__, __version__, cli

if __experimental__:
    runner = CliRunner(env={"AIRFLOW_DIAGRAMS__EXPERIMENTAL": "true"})
else:
    runner = CliRunner()

STDOUT_LINES = (
    "ℹ️ Retrieving Airflow DAGs...",
    "  ℹ️ Retrieving Airflow Tasks for Airflow DAG test_dag...",
    "🪄 Processing Airflow DAG test_dag...",
    "  🪄 Processing Airflow Task test_task (module.operators.path.ClassNameOperator) with downstream tasks []...",
    "  🔮No match found! Falling back to programming.flowchart.Action.",
    "  🪄 Processing Airflow Task test_task_real (airflow.providers.amazon.aws.operators.s3.S3CreateBucketOperator) with downstream tasks []...",
    "  🔮Found match aws.storage.SimpleStorageServiceS3Bucket.",
    "🎨Generated diagrams file generated/test_dag_diagrams.py.",
    "Done. 🎉",
)


def strip_white_space(*strings) -> str:
    """
    Strip white spaces (including new line and tabs) from a string.

    :params strings: The strings to strip the white spaces from.

    :returns: the stripped string.
    """
    return "".join(strings).replace(" ", "").replace("\t", "").replace("\n", "")


@pytest.fixture()
def _mock_dag(airflow_api_tree):
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
            dict(
                class_ref=dict(
                    module_path="airflow.providers.amazon.aws.operators.s3",
                    class_name="S3CreateBucketOperator",
                ),
                task_id="test_task_real",
                downstream_task_ids=[],
            ),
        ],
    )


def test_version():
    """Test printing version"""
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" == result.stdout


@pytest.mark.skipif(
    __experimental__,
    reason="Only run test when experimental features are disabled.",
)
@pytest.mark.usefixtures("_mock_dag")
def test_generate():
    """Test end-to-end"""
    result = runner.invoke(cli.app, ["generate", "--output-path", "generated/"])
    assert result.exit_code == 0
    assert strip_white_space(*STDOUT_LINES) == strip_white_space(result.stdout)


@pytest.mark.skipif(
    __experimental__,
    reason="Only run test when experimental features are disabled.",
)
@pytest.mark.usefixtures("_mock_dag")
def test_generate_with_progress():
    """Test end-to-end"""
    result = runner.invoke(
        cli.app,
        ["generate", "--output-path", "generated/", "--progress"],
    )
    assert result.exit_code == 0
    assert strip_white_space(*STDOUT_LINES) == strip_white_space(result.stdout)


@pytest.mark.skipif(
    not __experimental__,
    reason="Only run test when experimental features are enabled.",
)
@pytest.mark.usefixtures("_mock_dag")
def test_generate_experimental():
    """Test end-to-end with experimental features enabled"""
    result = runner.invoke(cli.app, ["generate", "--output-path", "generated/"])
    assert result.exit_code == 0
    assert strip_white_space(
        "🧪Running with experimental features...",
        *STDOUT_LINES,
    ) == strip_white_space(result.stdout)


@pytest.mark.usefixtures("_mock_dag")
def test_generate_with_verbose():
    """Test that logging level is DEBUG"""
    result = runner.invoke(
        cli.app,
        ["generate", "--output-path", "generated/", "--verbose"],
    )
    assert result.exit_code == 0
    assert result.stdout.startswith("💬Running with verbose output...")


@pytest.mark.skipif(
    __experimental__,
    reason="Only run test when experimental features are disabled.",
)
@pytest.mark.order(after="test_download")
@pytest.mark.usefixtures("_mock_dag")
def test_generate_from_file():
    """Test generate from Airflow info file"""
    result = runner.invoke(
        cli.app,
        ["generate", "--output-path", "generated/", "-f", "generated/airflow_dags.yml"],
    )
    assert result.exit_code == 0
    assert strip_white_space(
        "📝Loading Airflow information from file...",
        *STDOUT_LINES[2:],
    ) == strip_white_space(result.stdout)


@pytest.mark.skipif(
    __experimental__,
    reason="Only run test when experimental features are disabled.",
)
@pytest.mark.usefixtures("_mock_dag")
def test_download():
    """Test downloading Airflow information"""
    result = runner.invoke(cli.app, ["download", "generated/airflow_dags.yml"])
    assert result.exit_code == 0
    assert strip_white_space(
        *STDOUT_LINES[:2],
        "📝Dumping to file...",
        STDOUT_LINES[-1],
    ) == strip_white_space(result.stdout)
