from dataclasses import dataclass
from typing import Optional

from airflow_client.client.api.dag_api import DAGApi
from airflow_client.client.api_client import ApiClient

from airflow_diagrams.class_ref import ClassRef


@dataclass
class AirflowTask:
    """Airflow task info used to be able to match with diagram class_refs and render."""

    class_ref: ClassRef
    task_id: str
    downstream_task_ids: list[str]

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

    def __str__(self) -> str:
        """
        Define pretty string reprenstation.

        :returns: the string representation of the Airflow DAG.
        """
        return f"Airflow DAG {self.dag_id}"

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
            )
            # TODO: Enable type checking when https://github.com/apache/airflow-client-python/issues/20 is fixed.
            for task in self.dag_api.get_tasks(self.dag_id, _check_return_type=False)[
                "tasks"
            ]
        ]


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
