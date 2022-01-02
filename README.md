# airflow-diagrams

[![PyPI version](https://img.shields.io/pypi/v/airflow-diagrams?style=for-the-badge)](https://pypi.org/project/airflow-diagrams/)
[![License](https://img.shields.io/pypi/l/airflow-diagrams?style=for-the-badge)](https://github.com/feluelle/airflow-diagrams/blob/master/LICENSE)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/airflow-diagrams?style=for-the-badge)](https://pypi.org/project/airflow-diagrams/)

> Auto-generated Diagrams from Airflow DAGs.

This project aims to easily visualise your [Airflow](https://github.com/apache/airflow) DAGs on service level
from providers like AWS, GCP, Azure, etc. via [diagrams](https://github.com/mingrammer/diagrams).

## 🚀 Get started

### Installation

To install it from [PyPI](https://pypi.org/) run:
```
pip install airflow-diagrams
```

### Usage

To use this auto-generator just run the following command:
```
airflow_diagrams generate
```
**Note:** *The default command is trying to authenticate to `http://localhost:8080/api/v1` via username `admin` and password `admin`. You can change those values via flags i.e. `-h`, `-u` or `-p`. Check out the help i.e. `--help` for more information.*

This will create a file like `<dag-id>_diagrams.py` which contains the definition to create a diagram. Run this file and you will get a rendered diagram.

Examples of generated diagrams can be found in the [examples](examples) directory.

## 🤔 How it Works

It connects via the [Airflow REST API](https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html) to your Airflow installation to retrieve DAGs (in case you don't specify a dag id) and Tasks to generate matching diagrams nodes.

## ❤️ Contributing

Contributions are very welcome. Please go ahead and raise an issue if you have one or open a PR. Thank you.
