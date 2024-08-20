import pytest
from pytest_mock import MockerFixture

from airflow_diagrams.airflow import AirflowApiTree


@pytest.fixture
def airflow_api_tree(mocker: MockerFixture) -> AirflowApiTree:
    """
    Mock the Airflow API.

    :returns: the Airflow API Tree object with no connection to the API.
    """
    mocker.patch("airflow_diagrams.airflow.DAGApi")
    return AirflowApiTree(api_client=mocker.ANY)
