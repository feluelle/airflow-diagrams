"""Creates random fake Airflow DAGs as yaml file."""

import argparse
import random

import yaml
from networkx import DiGraph, gnp_random_graph, to_dict_of_lists

from airflow_diagrams.airflow import AirflowTask
from airflow_diagrams.class_ref import ClassRef, retrieve_class_refs


def _retrieve_airflow_class_refs():
    class_refs = retrieve_class_refs(directory="generated/airflow/airflow")
    return list(
        filter(
            lambda class_ref: (
                class_ref.module_path.startswith("airflow.")
                and (
                    ".operators." in class_ref.module_path
                    or ".sensors." in class_ref.module_path
                    or ".transfers." in class_ref.module_path
                )
                and class_ref.class_name.endswith(("Operator", "Sensor"))
            ),
            class_refs,
        ),
    )


def _generate_airflow_tasks(class_refs: list[ClassRef]):
    graph = gnp_random_graph(len(class_refs), 0.05, directed=True)
    dag = DiGraph(
        [
            (
                str(class_refs[u]),
                str(class_refs[v]),
                {"weight": random.randint(-10, 10)},  # noqa: S311
            )
            for u, v in graph.edges()
            if u < v
        ],
    )
    tasks_with_downstream_tasks = to_dict_of_lists(dag)

    return tasks_with_downstream_tasks


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o")
    parser.add_argument("-a", action="store_true")
    args = parser.parse_args()

    class_refs = _retrieve_airflow_class_refs()

    if args.a:
        airflow_dags = dict(
            dag=[
                AirflowTask(
                    class_ref=ClassRef.from_string(key),
                    task_id=key,
                    downstream_task_ids=[],
                    group_name=None,
                )
                for key, value in _generate_airflow_tasks(class_refs).items()
            ],
        )
    else:
        airflow_dags = dict(
            random_dag=[
                AirflowTask(
                    class_ref=ClassRef.from_string(key),
                    task_id=key,
                    downstream_task_ids=value,
                    group_name=None,
                )
                for key, value in _generate_airflow_tasks(
                    random.choices(class_refs, k=20),  # noqa: S311
                ).items()
            ],
        )

    with open(args.o, "w") as file:
        yaml.dump(airflow_dags, file)
