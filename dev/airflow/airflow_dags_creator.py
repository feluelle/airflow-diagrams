"""Creates random fake Airflow DAGs as yaml file."""
import os
import random

import yaml
from networkx import DiGraph, gnp_random_graph, to_dict_of_lists

from airflow_diagrams import __location__
from airflow_diagrams.airflow import AirflowTask
from airflow_diagrams.class_ref import ClassRef, retrieve_class_refs


def _retrieve_airflow_class_refs():
    # Make sure to clone/download the airflow repo first into below directory
    # E.g. gh repo clone apache/airflow generated/airflow
    class_refs = retrieve_class_refs(directory="generated/airflow/airflow/providers/")
    return list(
        filter(
            lambda class_ref: (
                (
                    ".operators." in class_ref.module_path
                    or ".sensors." in class_ref.module_path
                    or ".transfers." in class_ref.module_path
                )
                and class_ref.class_name.endswith(("Operator", "Sensor"))
            ),
            class_refs,
        ),
    )


def _generate_airflow_tasks(n: int = 20):
    class_refs = random.choices(_retrieve_airflow_class_refs(), k=n)  # nosec
    graph = gnp_random_graph(n, 0.05, directed=True)
    dag = DiGraph(
        [
            (
                str(class_refs[u]),
                str(class_refs[v]),
                {"weight": random.randint(-10, 10)},  # nosec
            )
            for u, v in graph.edges()
            if u < v
        ],
    )
    tasks_with_downstream_tasks = to_dict_of_lists(dag)

    return [
        AirflowTask(
            class_ref=ClassRef.from_string(key),
            task_id=key,
            downstream_task_ids=value,
            group_name=None,
        )
        for key, value in tasks_with_downstream_tasks.items()
    ]


if __name__ == "__main__":
    airflow_dags = dict(
        random_dag=_generate_airflow_tasks(),
    )

    with open(
        os.path.join(__location__, "../generated/airflow_dags_random.yml"),
        "w",
    ) as file:
        yaml.dump(airflow_dags, file)
