from airflow_diagrams.airflow import AirflowDag, AirflowTask
from airflow_diagrams.class_ref import ClassRef


def test_airflow_dag_get_tasks(airflow_api_tree):
    """Test getting tasks from Airflow DAG"""
    dag_id = "test_dag"
    airflow_api_tree.dag_api.get_tasks.return_value = dict(
        tasks=[
            dict(
                class_ref=dict(
                    module_path="test_module",
                    class_name="test_class",
                ),
                task_id="test_task_1",
                downstream_task_ids=[],
                group_name=None,
            ),
            dict(
                class_ref=dict(
                    module_path="test_module",
                    class_name="test_class",
                ),
                task_id="test_task_2",
                downstream_task_ids=["test_task_1"],
                group_name=None,
            ),
        ],
    )
    assert airflow_api_tree.get_dags(dag_id=dag_id)[0].get_tasks() == [
        AirflowTask(
            class_ref=ClassRef(**task["class_ref"]),
            task_id=task["task_id"],
            downstream_task_ids=task["downstream_task_ids"],
            group_name=None,
        )
        for task in airflow_api_tree.dag_api.get_tasks.return_value["tasks"]
    ]


def test_airflow_api_tree_get_dags(airflow_api_tree):
    """Test getting dags from Airflow API Tree"""
    airflow_api_tree.dag_api.get_dags.return_value = dict(
        dags=[
            dict(
                dag_id="test_dag_1",
            ),
            dict(
                dag_id="test_dag_2",
            ),
        ],
    )
    assert airflow_api_tree.get_dags() == [
        AirflowDag(
            dag_id=dag["dag_id"],
            dag_api=airflow_api_tree.dag_api,
        )
        for dag in airflow_api_tree.dag_api.get_dags.return_value["dags"]
    ]


def test_airflow_api_tree_get_dags_with_dag_id(airflow_api_tree):
    """Test getting dag from Airflow API Tree"""
    dag_id = "test_dag"
    assert airflow_api_tree.get_dags(dag_id=dag_id) == [
        AirflowDag(dag_id=dag_id, dag_api=airflow_api_tree.dag_api),
    ]
    airflow_api_tree.dag_api.assert_not_called()


def test_airflow_dag_eq(airflow_api_tree):
    """Test Airflow DAG equality"""
    airflow_dag_kwargs = dict(dag_id="test_dag", dag_api=airflow_api_tree.dag_api)
    assert AirflowDag(**airflow_dag_kwargs) == AirflowDag(**airflow_dag_kwargs)
    assert AirflowDag(**airflow_dag_kwargs) != dict(**airflow_dag_kwargs)
