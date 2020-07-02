# airflow-diagrams

> Auto-generated Diagrams from Airflow DAGs.

This project aims to easily visualise you Airflow DAGs on service level 
from providers like AWS, GCP, Azure, etc.

## How-to-Use

To use this auto-generator just add the following two lines to your Airflow DAG (and run it):
```
from airflow_diagrams import generate_diagram_from_dag
generate_diagram_from_dag(dag=dag, diagram_file="diagram.py")
```
This will create a file called `diagram.py` which contains the definition to create a diagram.

Run this file and you will get a rendered diagram.

A working example can be found in [examples](examples/dags/test_dag.py).

## Contribute

This project is in a very early stage. And contributions are welcome <3.
The [mapping.json](airflow_diagrams/mapping.json) needs a lot more entries 
so the Diagram can be proper created for all kinds of Airflow DAGs.

## License

[MIT](LICENSE)
