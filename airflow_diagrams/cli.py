"""This module provides the airflow-diagrams CLI."""
import logging
import os
from typing import Optional

from airflow_client.client.api_client import ApiClient, Configuration
from typer import Exit, Option, Typer, colors, echo, secho

from airflow_diagrams import __app_name__, __version__
from airflow_diagrams.airflow import AirflowApiTree
from airflow_diagrams.class_ref import ClassRef, ClassRefMatcher
from airflow_diagrams.helper import (
    get_diagrams_class_refs,
    load_abbreviations,
    load_mappings,
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
    mapping_file: str = Option(
        None,
        "--mapping-file",
        "-m",
        help="The mapping file to use for static mapping from Airflow task to diagram node.",
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

    mappings: dict = load_mappings(mapping_file) if mapping_file else {}

    diagrams_class_refs: list[ClassRef] = get_diagrams_class_refs()

    abbreviations: dict = load_abbreviations()

    airflow_api_config = Configuration(host=host, username=username, password=password)
    with ApiClient(configuration=airflow_api_config) as api_client:
        airflow_api_tree = AirflowApiTree(api_client)
        for airflow_dag in airflow_api_tree.get_dags(dag_id):
            secho(f"ℹ️ Retrieved {airflow_dag}.", fg=colors.CYAN)
            matches_class_refs: set[ClassRef] = set()
            diagram_nodes: list[dict] = []
            diagram_edges: list[dict] = []
            for airflow_task in airflow_dag.get_tasks():
                secho(f"  ℹ️ Retrieved {airflow_task}.", fg=colors.CYAN)
                class_ref_matcher = ClassRefMatcher(
                    query=airflow_task.class_ref,
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
                match_class_ref: ClassRef = class_ref_matcher.match(mappings)
                secho(f"  🔮Found match {match_class_ref}.", fg=colors.MAGENTA)
                matches_class_refs.add(match_class_ref)
                diagram_nodes.append(
                    dict(
                        task_id=airflow_task.task_id,
                        class_name=match_class_ref.class_name,
                    ),
                )
                if airflow_task.downstream_task_ids:
                    diagram_edges.append(
                        dict(
                            task_id=airflow_task.task_id,
                            downstream_task_ids=airflow_task.downstream_task_ids,
                        ),
                    )

            output_file = os.path.join(output_path, f"{airflow_dag.dag_id}_diagrams.py")
            render_jinja(
                template_file="diagram.jinja2",
                context=dict(
                    diagram_class_refs=matches_class_refs,
                    diagram_name=airflow_dag.dag_id,
                    diagram_nodes=diagram_nodes,
                    diagram_edges=diagram_edges,
                ),
                output_file=output_file,
            )
            secho(f"🪄 Generated diagrams file {output_file}.", fg=colors.YELLOW)
        secho("Done. 🎉", fg=colors.GREEN)
