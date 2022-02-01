"""This module provides the airflow-diagrams CLI."""
import logging
import os
from pathlib import Path
from typing import Optional

import diagrams
from airflow_client.client.api_client import ApiClient, Configuration
from typer import Exit, Option, Typer, colors, echo, secho

from airflow_diagrams import __app_name__, __version__
from airflow_diagrams.airflow import AirflowApiTree
from airflow_diagrams.class_ref import ClassRef, ClassRefMatcher, retrieve_class_refs
from airflow_diagrams.diagrams import DiagramContext
from airflow_diagrams.utils import load_abbreviations, load_mappings

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


@app.command(
    help="Generates <airflow-dag-id>_diagrams.py in <output-path> directory which contains the definition to create a diagram. Run this file and you will get a rendered diagram.",
)
def generate(  # dead: disable
    dag_id: Optional[str] = Option(
        None,
        "--airflow-dag-id",
        "-d",
        help="The dag id from which to generate the diagram. By default it generates for all.",
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
    output_path: Path = Option(
        ".",
        "--output-path",
        "-o",
        help="The path to output the diagrams to.",
        exists=True,
        file_okay=False,
        writable=True,
    ),
    mapping_file: Path = Option(
        None,
        "--mapping-file",
        "-m",
        help="The mapping file to use for static mapping from Airflow task to diagram node. By default no mapping file is being used.",
        exists=True,
        dir_okay=False,
    ),
    verbose: bool = Option(
        False,
        "--verbose",
        "-v",
        help="Verbose output i.e. useful for debugging purposes.",
    ),
    label_wrap: Optional[str] = Option(
        None,
        "--label-wrap",
        "-lw",
        help="Specify either a number for label width or a separator to indicate when to wrap a label. By default it does not wrap labels.",
    ),
) -> None:
    if verbose:
        echo("💬 Running with verbose output..")
        logging.basicConfig(level=logging.DEBUG)

    mappings: dict = load_mappings(mapping_file) if mapping_file else {}

    diagrams_class_refs: list[ClassRef] = retrieve_class_refs(
        directory=f"{os.path.dirname(diagrams.__file__)}/",
    )

    abbreviations: dict = load_abbreviations()

    airflow_api_config = Configuration(host=host, username=username, password=password)
    with ApiClient(configuration=airflow_api_config) as api_client:
        airflow_api_tree = AirflowApiTree(api_client)

        for airflow_dag in airflow_api_tree.get_dags(dag_id):
            secho(f"ℹ️ Retrieved {airflow_dag}.", fg=colors.CYAN)
            diagram_context = DiagramContext(
                airflow_dag=airflow_dag,
                label_wrap=label_wrap,
            )

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
                diagram_context.push(
                    airflow_task=airflow_task,
                    node_class_ref=match_class_ref,
                )

            output_file = output_path / f"{airflow_dag.dag_id}_diagrams.py"
            diagram_context.render(output_file)
            secho(f"🪄 Generated diagrams file {output_file}.", fg=colors.YELLOW)

        secho("Done. 🎉", fg=colors.GREEN)
