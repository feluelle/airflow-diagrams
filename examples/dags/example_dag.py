from airflow.models.dag import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.dates import days_ago

from airflow_diagrams import generate_diagram_from_dag

with DAG('example_dag', schedule_interval=None, default_args=dict(start_date=days_ago(2))) as dag:
    DummyOperator(task_id='run_this_1') >> [
        DummyOperator(task_id='run_this_2a'), DummyOperator(task_id='run_this_2b')
    ] >> DummyOperator(task_id='run_this_3')

generate_diagram_from_dag(dag=dag, diagram_file=f"../diagrams/{dag.dag_id}.py")
