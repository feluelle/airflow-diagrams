# airflow-diagrams

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/feluelle/airflow-diagrams/master.svg)](https://results.pre-commit.ci/latest/github/feluelle/airflow-diagrams/master)
[![PyPI version](https://img.shields.io/pypi/v/airflow-diagrams)](https://pypi.org/project/airflow-diagrams/)
[![License](https://img.shields.io/pypi/l/airflow-diagrams)](https://github.com/feluelle/airflow-diagrams/blob/master/LICENSE)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/airflow-diagrams)](https://pypi.org/project/airflow-diagrams/)

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

ℹ️ At first it connects, by using the official [Apache Airflow Python Client](https://github.com/apache/airflow-client-python), to your Airflow installation to retrieve all DAGs (in case you don't specify any `dag_id`) and all Tasks for the DAG(s).

🔮 Then it tries to find a diagram node for every DAGs task, by using [Fuzzy String Matching](https://github.com/seatgeek/thefuzz), that matches the most. If you are unhappy about the match you can also provide a `mapping.yml` file to statically map from Airflow task to diagram node.

🪄 Lastly it renders the results into a python file which can then be executed to retrieve the rendered diagram. 🎉

## ❤️ Contributing

Contributions are very welcome. Please go ahead and raise an issue if you have one or open a PR. Thank you.
