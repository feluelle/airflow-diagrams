from pathlib import Path

import pytest

from airflow_diagrams.airflow import AirflowDag, AirflowTask
from airflow_diagrams.class_ref import ClassRef
from airflow_diagrams.diagrams import (
    DiagramContext,
    DiagramEdge,
    DiagramNode,
    to_var,
    wrap_str,
)


@pytest.fixture
def airflow_task():
    return AirflowTask(
        class_ref=ClassRef(
            module_path="foo",
            class_name="Bar",
        ),
        task_id="foo_bar",
        downstream_task_ids=["fizz"],
    )


@pytest.fixture
def airflow_dag(mocker):
    return AirflowDag(dag_id="foo", dag_api=mocker.ANY)


def test_to_var():
    """Test converting to python variable"""
    var = to_var("foo-bar")
    assert "-" not in var and "." not in var
    assert var.startswith("_")


def test_wrap_str__indicator_number():
    """Test wrapping a string based on number"""
    assert wrap_str("foobarfoobar", "10") == "foobarfoob\\nar"


def test_wrap_str__indicator_separator():
    """Test wrapping a string based on separator"""
    assert wrap_str("foobarfoobar", "foo") == "\\nbar\\nbar"


def test_diagram_node(airflow_task):
    """Test diagram node initialisation"""
    class_name = "DiagramsBar"
    label_wrap = "_"
    diagram_node = DiagramNode(
        task=airflow_task,
        class_name=class_name,
        label_wrap=label_wrap,
    )
    assert diagram_node.label == wrap_str(airflow_task.task_id, label_wrap)
    assert diagram_node.class_name == class_name
    assert diagram_node.variable == to_var(airflow_task.task_id)


def test_diagram_edge(airflow_task):
    """Test diagram edge initialisation"""
    diagram_edge = DiagramEdge(task=airflow_task)
    assert diagram_edge.variable == to_var(airflow_task.task_id)
    assert list(diagram_edge.downstream_variables) == list(
        map(
            to_var,
            airflow_task.downstream_task_ids,
        ),
    )


def test_diagram_context(mocker, airflow_dag, airflow_task):
    """Test diagram context initialisation, pushing and rendering"""
    diagram_context = DiagramContext(airflow_dag=airflow_dag, label_wrap="_")
    assert diagram_context.airflow_dag
    assert diagram_context.label_wrap

    diagram_context.push(
        airflow_task=airflow_task,
        node_class_ref=ClassRef.from_string("foo.bar"),
    )
    assert diagram_context.matched_class_refs
    assert diagram_context.nodes
    assert diagram_context.edges

    render_jinja = mocker.patch("airflow_diagrams.diagrams.render_jinja")
    output_file = Path("./foo.py")
    diagram_context.render(output_file)
    render_jinja.assert_called_once_with(
        template_file="diagram.jinja2",
        context=dict(
            class_refs=diagram_context.matched_class_refs,
            name=diagram_context.airflow_dag.dag_id,
            nodes=diagram_context.nodes,
            edges=diagram_context.edges,
        ),
        output_file=output_file.as_posix(),
    )
