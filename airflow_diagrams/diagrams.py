from dataclasses import dataclass
from hashlib import md5
from os.path import dirname
from pathlib import Path
from textwrap import wrap
from typing import Optional

from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader
from jinja2.runtime import StrictUndefined

from airflow_diagrams.airflow import AirflowTask
from airflow_diagrams.class_ref import ClassRef


def to_var(string: str) -> str:
    """
    Convert a string to a valid python variable name.

    :params string: The string to convert.
    :returns: a valid python variable name.
    """
    return f"_{md5(string.encode()).hexdigest()}"  # nosec


def wrap_str(string: str, indicator: str) -> str:
    """
    Wrap a string with newline chars based on indicator.

    :params string: The string to wrap.
    :params indicator: Specify either a number for width or a separator to indicate when to wrap.
    :returns: the wrapped string.
    """
    if indicator.isdigit():
        return "\\n".join(wrap(string, int(indicator), break_on_hyphens=False))
    return "\\n".join(string.split(indicator))


def render_jinja(template_file: str, context: dict, output_file: str) -> None:
    """
    Render the context, given a template file, to a file.

    :param template_file: The file containing the template to render.
    :param context: The context to pass to the template_file.
    :param output_file: The file to output the rendered version.
    """
    (
        Environment(
            loader=FileSystemLoader(dirname(__file__)),
            undefined=StrictUndefined,
            autoescape=True,
        )
        .get_template(template_file)
        .stream(**context)
        .dump(output_file)
    )


@dataclass
class _DiagramItem:
    """A generic item in a diagram representation."""

    _id: str

    def get_label(self, label_wrap: Optional[str]) -> str:  # dead: disable
        """
        Get the label of the item rendered.

        :params label_wrap: Specify either a number for label width or a separator to indicate when to wrap a label.
        :returns: the label.
        """
        if label_wrap:
            return wrap_str(self._id, label_wrap)
        return self._id

    def get_variable(self) -> str:  # dead: disable
        """
        Get the variable of the item rendered.

        :returns: the variable.
        """
        return to_var(self._id)


@dataclass(unsafe_hash=True)
class DiagramCluster(_DiagramItem):
    """The cluster object in a diagram representation."""


@dataclass
class DiagramNode(_DiagramItem):
    """The node object in a diagram representation."""

    class_name: str
    cluster: Optional[DiagramCluster]


@dataclass
class DiagramEdge(_DiagramItem):
    """The edge object in a diagram representation."""

    _downstream_ids: list[str]

    def get_downstream_variables(self) -> list[str]:  # dead: disable
        """
        Get the downstream variables of the edge rendered.

        :returns: downstream variables.
        """
        return list(map(to_var, self._downstream_ids))


class DiagramContext:
    """
    The whole diagram context in a diagram representation.

    :params airflow_dag_id: The airflow dag id to render the context for.
    """

    def __init__(self, airflow_dag_id: str) -> None:
        self.airflow_dag_id = airflow_dag_id
        self.matched_class_refs: set[ClassRef] = set()
        self.nodes: list[DiagramNode] = []
        self.edges: list[DiagramEdge] = []
        self.clusters: set[DiagramCluster] = set()

    def push(self, airflow_task: AirflowTask, node_class_ref: ClassRef) -> None:
        """
        Pushes Airflow task information to the context.

        :params airflow_task: The airflow task from which to push.
        :params node_class_ref: The class reference of the node in the diagram.
        """
        self.matched_class_refs.add(node_class_ref)

        cluster = (
            DiagramCluster(_id=airflow_task.group_name)
            if airflow_task.group_name
            else None
        )

        node = DiagramNode(
            _id=airflow_task.task_id,
            class_name=node_class_ref.class_name,
            cluster=cluster,
        )
        self.nodes.append(node)

        if airflow_task.downstream_task_ids:
            edge = DiagramEdge(
                _id=airflow_task.task_id,
                _downstream_ids=airflow_task.downstream_task_ids,
            )
            self.edges.append(edge)

        if cluster:
            self.clusters.add(cluster)

    def render(self, output_file: Path, label_wrap: Optional[str]) -> None:
        """
        Render the airflow dag with tasks context to the diagram.

        :params output_file: The output file path to write the diagrams file to.
        :params label_wrap: Specify either a number for label width or a separator to indicate when to wrap a label.
        """
        render_jinja(
            template_file="diagram.jinja2",
            context=dict(
                class_refs=self.matched_class_refs,
                name=self.airflow_dag_id,
                nodes=self.nodes,
                edges=self.edges,
                clusters=self.clusters,
                label_wrap=label_wrap,
            ),
            output_file=output_file.as_posix(),
        )
