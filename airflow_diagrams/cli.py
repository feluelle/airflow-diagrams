"""This module provides the airflow-diagrams CLI."""
import logging
import os
from typing import Optional

from typer import Exit, Option, Typer, colors, echo, secho

from airflow_diagrams import __app_name__, __version__
from airflow_diagrams.helper import (
    AirflowClient,
    ClassRef,
    ClassRefMatcher,
    get_diagrams_class_refs,
    load_abbreviations,
    render_jinja,
)

app = Typer()


def _version_callback(value: bool) -> None:
    if value:
        echo(f"{__app_name__} v{__version__}")
        raise Exit()


@app.callback()
def main(
    version: Optional[bool] = Option(  # dead: disable
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    return


@app.command()
def generate(  # dead: disable
    dag_id: str = Option(
        None,
        "--airflow-dag-id",
        "-d",
        help="The dag id from which to generate the diagram.",
    ),
    host: str = Option(
        "http://localhost:8080/api/v1",
        "--airflow-host",
        "-h",
        help="The host of the airflow rest api from where to retrieve the dag tasks information.",
    ),
    username: str = Option(
        "admin",
        "--airflow-username",
        "-u",
        help="The username of the airflow rest api.",
    ),
    password: str = Option(
        "admin",
        "--airflow-password",
        "-p",
        help="The password of the airflow rest api.",
    ),
    output_path: str = Option(
        ".",
        "--output-path",
        "-o",
        help="The path to output the diagrams to.",
    ),
    verbose: bool = Option(
        False,
        "--verbose",
        "-v",
        help="Verbose output i.e. useful for debugging purposes.",
    ),
) -> None:
    if verbose:
        logging.basicConfig(level=logging.DEBUG)

    abbreviations = load_abbreviations()

    diagrams_class_refs: list[ClassRef] = get_diagrams_class_refs()

    airflow_client = AirflowClient(host, username, password)
    airflow_dags = [dag_id] if dag_id else airflow_client.get_dags()
    for airflow_dag_id in airflow_dags:
        matches_class_refs: list[ClassRef] = []
        diagram_nodes: list = []
        diagram_edges: list = []

        for airflow_task in airflow_client.get_tasks(airflow_dag_id):

            airflow_class_ref: ClassRef = ClassRef(**airflow_task["class_ref"])

            class_ref_matcher = ClassRefMatcher(
                query=airflow_class_ref,
                choices=diagrams_class_refs,
                query_options=dict(
                    removesuffixes=["Operator", "Sensor"],
                    replaceabbreviations=abbreviations,
                ),
                choices_options=dict(
                    removesuffixes=[],
                    replaceabbreviations=abbreviations,
                ),
            )
            match_class_ref: ClassRef = class_ref_matcher.match()
            secho(
                f"Found match {match_class_ref} for task {airflow_class_ref}.",
                fg=colors.CYAN,
            )
            matches_class_refs.append(match_class_ref)
            diagram_nodes.append(
                dict(
                    task_id=airflow_task["task_id"],
                    class_name=match_class_ref.class_name,
                ),
            )
            diagram_edges.append(
                dict(
                    task_id=airflow_task["task_id"],
                    downstream_task_ids=airflow_task["downstream_task_ids"],
                ),
            )

        output_file = os.path.join(output_path, f"{airflow_dag_id}_diagrams.py")
        render_jinja(
            template_file="diagram.jinja2",
            context=dict(
                diagram_class_refs=matches_class_refs,
                diagram_name=airflow_dag_id,
                diagram_nodes=diagram_nodes,
                diagram_edges=diagram_edges,
            ),
            output_file=output_file,
        )

        secho(
            f"Successfully generated diagrams file {output_file} from dag with id {airflow_dag_id}.",
            fg=colors.GREEN,
        )
