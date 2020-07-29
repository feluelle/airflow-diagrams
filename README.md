# airflow-diagrams

[![PyPI version](https://img.shields.io/pypi/v/airflow-diagrams?style=for-the-badge)](https://pypi.org/project/airflow-diagrams/)
[![License](https://img.shields.io/pypi/l/airflow-diagrams?style=for-the-badge)](https://github.com/feluelle/airflow-diagrams/blob/master/LICENSE)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/airflow-diagrams?style=for-the-badge)](https://pypi.org/project/airflow-diagrams/)

> Auto-generated Diagrams from Airflow DAGs.

This project aims to easily visualise your [Airflow](https://github.com/apache/airflow) DAGs on service level 
from providers like AWS, GCP, Azure, etc. via [diagrams](https://github.com/mingrammer/diagrams).

## Installation

To install it from [PyPI](https://pypi.org/) run:
```
pip install airflow-diagrams
```

## How to Use

To use this auto-generator just add the following two lines to your Airflow DAG (and run it):
```python
from airflow_diagrams import generate_diagram_from_dag
generate_diagram_from_dag(dag=dag, diagram_file="diagram.py")
```
This will create a file called `diagram.py` which contains the definition to create a diagram.

Run this file and you will get a rendered diagram.

A working example can be found in [examples](examples) with the [example_dag](examples/dags/example_dag.py) generating 
the [diagram](examples/diagrams/example_dag.py) ([rendered](examples/diagrams/example_dag.png) version).

## How it Works

It iterates through all operators in the DAG and decides based on a [mapping](airflow_diagrams/mapping.json) which diagram node to display for each type of operator.

## Contributing

Contributions are welcome <3. Please go ahead and raise an issue if you have one or open a PR. Thank you. :)
