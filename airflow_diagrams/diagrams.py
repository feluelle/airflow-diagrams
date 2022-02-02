from hashlib import md5
from os.path import dirname
from pathlib import Path
from textwrap import wrap
from typing import Optional

from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader
from jinja2.runtime import StrictUndefined

from airflow_diagrams.airflow import AirflowDag, AirflowTask
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


class DiagramNode:
    """
    The node object in a diagram representation.

    :params task: The airflow task to display node information for.
    :params class_name: The final diagrams class name.
    """

    def __init__(self, task: AirflowTask, class_name: str, **kwargs) -> None:
        label_wrap = kwargs.pop("label_wrap")

        self.label = wrap_str(task.task_id, label_wrap) if label_wrap else task.task_id
        self.class_name = class_name
        self.variable = to_var(task.task_id)
        self.cluster_variable = to_var(task.group_name) if task.group_name else None


class DiagramEdge:
    """
    The edge object in a diagram representation.

    :params task: The airflow task to display edge information for.
    """

    def __init__(self, task: AirflowTask) -> None:
        self.variable = to_var(task.task_id)
        self.downstream_variables = map(
            to_var,
            task.downstream_task_ids,
        )


class DiagramCluster:
    """
    The cluster object in a diagram representation.

    :params task: The airflow task to display cluster information for.
    """

    def __init__(self, task: AirflowTask, **kwargs) -> None:
        label_wrap = kwargs.pop("label_wrap")

        assert task.group_name  # nosec
        self.label = (
            wrap_str(task.group_name, label_wrap) if label_wrap else task.group_name
        )
        self.variable = to_var(task.group_name)

    def __hash__(self) -> int:
        """
        Build a hash based on all attributes.

        :returns: a hash of all attributes.
        """
        return hash(self.label) ^ hash(self.variable)

    def __eq__(self, __o: object) -> bool:
        """
        Check cluster equality.

        :params __o: The object to check against.

        :returns: True if the cluster is the same, if not False.
        """
        if isinstance(__o, DiagramCluster):
            return self.label == __o.label and self.variable == __o.variable
        return False


class DiagramContext:
    """
    The whole diagram context in a diagram representation.

    :params airflow_dag: The airflow dag to render the context for.
    :params label_wrap: Wrap labels on given indicator.
    """

    def __init__(self, airflow_dag: AirflowDag, label_wrap: Optional[str]) -> None:
        self.airflow_dag = airflow_dag
        self.label_wrap = label_wrap
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

        self.nodes.append(
            DiagramNode(
                task=airflow_task,
                class_name=node_class_ref.class_name,
                label_wrap=self.label_wrap,
            ),
        )

        if airflow_task.downstream_task_ids:
            self.edges.append(DiagramEdge(task=airflow_task))

        if airflow_task.group_name:
            self.clusters.add(
                DiagramCluster(task=airflow_task, label_wrap=self.label_wrap),
            )

    def render(self, output_file: Path) -> None:
        """
        Render the airflow dag with tasks context to the diagram.

        :params output_file: The output file path to write the diagrams file to.
        """
        render_jinja(
            template_file="diagram.jinja2",
            context=dict(
                class_refs=self.matched_class_refs,
                name=self.airflow_dag.dag_id,
                nodes=self.nodes,
                edges=self.edges,
                clusters=self.clusters,
            ),
            output_file=output_file.as_posix(),
        )
