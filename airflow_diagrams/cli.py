"""This module provides the airflow-diagrams CLI."""
import logging
import os
import re
from pathlib import Path
from typing import Optional

import diagrams
import yaml
from rich import print as rprint
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from rich.traceback import install
from typer import Argument, Exit, Option

from airflow_diagrams import __app_name__, __version__
from airflow_diagrams.airflow import retrieve_airflow_info
from airflow_diagrams.class_ref import (
    ClassRef,
    ClassRefMatcher,
    MatchNotFoundError,
    retrieve_class_refs,
)
from airflow_diagrams.custom_typer import CustomTyper
from airflow_diagrams.diagrams import DiagramContext
from airflow_diagrams.utils import load_abbreviations, load_mappings

install(max_frames=1)

app = CustomTyper()


def _version_callback(value: bool) -> None:
    if value:
        print(f"{__app_name__} v{__version__}")
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
        help="Specify either a number for label width or a separator to indicate when to wrap a label. By default it does not wrap labels.",
    ),
    progress_bar: bool = Option(
        False,
        "--progress",
        help="Specify whether to show a progress bar or not. By default it does not show progress.",
    ),
    from_file: Path = Option(
        None,
        "--from-file",
        "-f",
        help="The file to read Airflow information from. By default it does not read Airflow info from file.",
        exists=True,
        dir_okay=False,
    ),
    export_matches: Path = Option(
        None,
        "--export-matches",
        help="Exports matches to file. This file can be used as mapping file. By default it is not being exported.",
    ),
) -> None:
    if verbose:
        rprint("💬Running with verbose output...")
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler()],
        )
        install(max_frames=0)

    mappings: dict = load_mappings(mapping_file) if mapping_file else {}

    diagrams_class_refs: list[ClassRef] = retrieve_class_refs(
        directory=os.path.dirname(diagrams.__file__),
    )

    abbreviations: dict = load_abbreviations()

    airflow_info_dict = {}
    if from_file:
        rprint("[yellow]📝Loading Airflow information from file...")
        with open(from_file, "r") as file:
            airflow_info = yaml.unsafe_load(file)

        total = len(airflow_info.keys())
        for airflow_dag_id, airflow_tasks in airflow_info.items():
            total += len(airflow_tasks)
            airflow_info_dict[airflow_dag_id] = airflow_tasks
    else:
        rprint("[cyan]ℹ️ Retrieving Airflow DAGs...")
        airflow_info = retrieve_airflow_info(dag_id, host, username, password)
        airflow_dags = next(airflow_info)

        total = len(airflow_dags)
        with Progress(
            SpinnerColumn(),
            *Progress.get_default_columns(),
            "[yellow]Elapsed:",
            TimeElapsedColumn(),
            transient=True,
            disable=not progress_bar,
        ) as progress:
            task_requests = progress.add_task(
                "[green]Downloading..",
                total=len(airflow_dags),
            )

            for airflow_dag_id, airflow_tasks in airflow_info:
                rprint(
                    f"[cyan dim]  ℹ️ Retrieving Airflow Tasks for Airflow DAG {airflow_dag_id}...",
                )
                total += len(airflow_tasks)
                airflow_info_dict[airflow_dag_id] = airflow_tasks
                progress.advance(task_requests)

    if export_matches:
        matches: dict[str, str] = {}

    with Progress(
        SpinnerColumn(),
        *Progress.get_default_columns(),
        "[yellow]Elapsed:",
        TimeElapsedColumn(),
        transient=True,
        disable=not progress_bar,
    ) as progress:
        task_processing = progress.add_task("[green]Processing..", total=total)

        for airflow_dag_id, airflow_tasks in airflow_info_dict.items():
            rprint(f"[blue]🪄 Processing Airflow DAG {airflow_dag_id}...")
            diagram_context = DiagramContext(airflow_dag_id)

            for airflow_task in airflow_tasks:
                rprint(f"[blue dim]  🪄 Processing {airflow_task}...")
                class_ref_matcher = ClassRefMatcher(
                    query=airflow_task.class_ref,
                    query_cleanup=lambda query_str: (
                        query_str.removeprefix("airflow.providers.")
                        .replace(".operators.", ".")
                        .replace(".sensors.", ".")
                        .replace(".transfers.", ".")
                        .removesuffix("Operator")
                        .removesuffix("Sensor")
                    ),
                    choices=diagrams_class_refs,
                    choice_cleanup=lambda choice_str: (
                        # The 2nd level of diagrams module path is irrelevant for matching
                        re.sub(r"\.\w+\.", ".", choice_str)
                    ),
                    abbreviations=abbreviations,
                )
                try:
                    match_class_ref = class_ref_matcher.match(mappings)
                    rprint(f"[magenta dim]  🔮Found match {match_class_ref}.")
                except MatchNotFoundError as error:
                    match_class_ref = ClassRef(
                        module_path="programming.flowchart",
                        class_name="Action",
                    )
                    rprint(f"[red dim]  🔮{error} Falling back to {match_class_ref}.")
                if export_matches:
                    matches[str(class_ref_matcher.query)] = str(match_class_ref)
                diagram_context.push(
                    airflow_task=airflow_task,
                    node_class_ref=match_class_ref,
                )
                progress.advance(task_processing)

            output_file = output_path / f"{airflow_dag_id}_diagrams.py"
            diagram_context.render(output_file, label_wrap)
            rprint(f"[yellow]🎨Generated diagrams file {output_file}.")
            progress.advance(task_processing)

    if export_matches:
        with open(export_matches, "w") as file:
            yaml.safe_dump(matches, file)

    rprint("[green]Done. 🎉")


@app.command(help="Download Airflow Information to file.")
def download(  # dead: disable
    output_file: Path = Argument(
        ...,
        help="The file to download airflow information to.",
        writable=True,
    ),
    dag_id: Optional[str] = Option(
        None,
        "--airflow-dag-id",
        "-d",
        help="The dag id for which to retrieve airflow information. By default it retrieves for all.",
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
    progress_bar: bool = Option(
        False,
        "--progress",
        help="Specify whether to show a progress bar or not. By default it does not show progress.",
    ),
) -> None:
    rprint("[cyan]ℹ️ Retrieving Airflow DAGs...")
    airflow_info = retrieve_airflow_info(dag_id, host, username, password)
    airflow_dags = next(airflow_info)

    airflow_info_dict = {}
    with Progress(
        SpinnerColumn(),
        *Progress.get_default_columns(),
        "[yellow]Elapsed:",
        TimeElapsedColumn(),
        transient=True,
        disable=not progress_bar,
    ) as progress:
        task_requests = progress.add_task(
            "[green]Downloading..",
            total=len(airflow_dags),
        )

        for airflow_dag_id, airflow_tasks in airflow_info:
            rprint(
                f"[cyan dim]  ℹ️ Retrieving Airflow Tasks for Airflow DAG {airflow_dag_id}...",
            )
            airflow_info_dict[airflow_dag_id] = airflow_tasks
            progress.advance(task_requests)

    rprint("[yellow]📝Dumping to file...")
    with open(output_file, "w") as file:
        yaml.dump(airflow_info_dict, file)

    rprint("[green]Done. 🎉")
