import re
from dataclasses import dataclass
from typing import Generator, Optional

from airflow_client.client.api.dag_api import DAGApi
from airflow_client.client.api_client import ApiClient, Configuration

from airflow_diagrams.class_ref import ClassRef
from airflow_diagrams.utils import experimental


@dataclass
class AirflowTask:
    """Airflow task info used to be able to match with diagram class_refs and render."""

    class_ref: ClassRef
    task_id: str
    downstream_task_ids: list[str]
    group_name: Optional[str]

    def __hash__(self) -> int:
        """
        Build a hash based on all attributes.

        :returns: a hash of all attributes.
        """
        return (
            hash(self.class_ref)
            ^ hash(self.task_id)
            ^ hash(
                downstream_task_id for downstream_task_id in self.downstream_task_ids
            )
            ^ hash(self.group_name)
        )

    def __str__(self) -> str:
        """
        Define pretty string reprenstation.

        :returns: the string representation of the Airflow Task.
        """
        return f"Airflow Task {self.task_id} ({self.class_ref}) with downstream tasks {self.downstream_task_ids}"


class AirflowDag:
    """Retrieve Airflow DAG information."""

    def __init__(self, dag_id: str, dag_api: DAGApi) -> None:
        self.dag_id = dag_id
        self.dag_api = dag_api

    def __eq__(self, __o: object) -> bool:
        """
        Check dag equality.

        :params __o: The object to check against.

        :returns: True if the dag_id is the same, if not False.
        """
        if isinstance(__o, AirflowDag):
            return self.dag_id == __o.dag_id
        return False

    def get_tasks(self) -> list[AirflowTask]:
        """
        Retrieve Airflow Tasks from the dag api.

        :returns: a list of Airflow Tasks
        """
        return [
            AirflowTask(
                class_ref=ClassRef(**task["class_ref"]),
                task_id=task["task_id"],
                downstream_task_ids=task["downstream_task_ids"],
                group_name=None,
            )
            # TODO: Enable type checking when https://github.com/apache/airflow-client-python/issues/20 is fixed.
            for task in self.dag_api.get_tasks(self.dag_id, _check_return_type=False)[
                "tasks"
            ]
        ]


@experimental
def transfer_nodes(tasks: list[AirflowTask]) -> None:
    """
    Transfer Nodes replaces an Airflow transfer task by two tasks i.e. source & destination clustered.

    :param tasks: The tasks to modify.
    """
    transfer_tasks = [
        (task, match.groups())
        for task in tasks
        if task.class_ref.module_path
        and ".transfers." in task.class_ref.module_path
        and (match := re.search(r"(\w+)To(\w+)", task.class_ref.class_name))
    ]

    for task, (source_class_name, destination_class_name) in transfer_tasks:
        source_task_id = f"[SOURCE] {task.task_id}"
        destination_task_id = f"[DESTINATION] {task.task_id}"
        source = AirflowTask(
            class_ref=ClassRef(
                module_path=None,  # We don't know if the original module_path belongs to source or destination
                class_name=source_class_name,
            ),
            task_id=source_task_id,
            downstream_task_ids=[destination_task_id],
            group_name=task.task_id,
        )
        destination = AirflowTask(
            class_ref=ClassRef(
                module_path=None,  # We don't know if the original module_path belongs to source or destination
                class_name=destination_class_name,
            ),
            task_id=destination_task_id,
            downstream_task_ids=task.downstream_task_ids,
            group_name=task.task_id,
        )
        tasks.extend([source, destination])
        tasks.remove(task)

    transfer_task_ids = list(map(lambda task: task[0].task_id, transfer_tasks))
    for t_idx, t in enumerate(tasks):
        for dt_idx, dt_id in enumerate(t.downstream_task_ids):
            if dt_id in transfer_task_ids:
                tasks[t_idx].downstream_task_ids[dt_idx] = f"[SOURCE] {dt_id}"


class AirflowApiTree:
    """Retrieve Airflow Api information as a Tree."""

    def __init__(self, api_client: ApiClient) -> None:
        self.dag_api = DAGApi(api_client)

    def get_dags(self, dag_id: Optional[str] = None) -> list[AirflowDag]:
        """
        Retrieve Airflow DAGs from the dag api.

        :params dag_id: A dag_id to retrieve the dag for.

        :returns: a list of Airflow DAGs
        """
        if dag_id:
            return [AirflowDag(dag_id=dag_id, dag_api=self.dag_api)]
        return [
            AirflowDag(
                dag_id=dag["dag_id"],
                dag_api=self.dag_api,
            )
            for dag in self.dag_api.get_dags()["dags"]
        ]


def retrieve_airflow_info(
    dag_id: Optional[str],
    host: str,
    username: str,
    password: str,
) -> Generator:
    """
    Retrieve Airflow Information from Airflow API.

    :params dag_id: The dag id for which to retrieve airflow information. By default it retrieves for all.
    :params host: The host of the airflow rest api from where to retrieve the dag tasks information.
    :params username: The username of the airflow rest api.
    :params password: The password of the airflow rest api.

    :returns: a generator of Airflow information.
    """
    airflow_api_config = Configuration(host=host, username=username, password=password)
    with ApiClient(configuration=airflow_api_config) as api_client:
        airflow_api_tree = AirflowApiTree(api_client)

        airflow_dags = airflow_api_tree.get_dags(dag_id)
        yield airflow_dags

        for airflow_dag in airflow_dags:
            airflow_tasks = airflow_dag.get_tasks()
            yield airflow_dag.dag_id, airflow_tasks
