# airflow-diagrams

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/feluelle/airflow-diagrams/main.svg)](https://results.pre-commit.ci/latest/github/feluelle/airflow-diagrams/main)
![test workflow](https://github.com/feluelle/airflow-diagrams/actions/workflows/test.yml/badge.svg)
![codeql-analysis workflow](https://github.com/feluelle/airflow-diagrams/actions/workflows/codeql-analysis.yml/badge.svg)
[![codecov](https://codecov.io/gh/feluelle/airflow-diagrams/branch/main/graph/badge.svg?token=J8UEP8IVY4)](https://codecov.io/gh/feluelle/airflow-diagrams)
[![PyPI version](https://img.shields.io/pypi/v/airflow-diagrams)](https://pypi.org/project/airflow-diagrams/)
[![License](https://img.shields.io/pypi/l/airflow-diagrams)](https://github.com/feluelle/airflow-diagrams/blob/main/LICENSE)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/airflow-diagrams)](https://pypi.org/project/airflow-diagrams/)
[![PyPI version](https://img.shields.io/pypi/dm/airflow-diagrams)](https://pypi.org/project/airflow-diagrams/)

> Auto-generated Diagrams from Airflow DAGs. 🔮 🪄

This project aims to easily visualise your [Airflow](https://github.com/apache/airflow) DAGs on service level
from providers like AWS, GCP, Azure, etc. via [diagrams](https://github.com/mingrammer/diagrams).

![demo](assets/images/demo.svg)

Before | After
--- | ---
![dag](assets/images/dbt_dag.png) | ![diagram](assets/images/dbt_diagram.png)

## 🚀 Get started

To install it from [PyPI](https://pypi.org/) run:

```console
pip install airflow-diagrams
```

> **_NOTE:_** Make sure you have [Graphviz](https://www.graphviz.org/) installed.

Then just call it like this:

![usage](assets/images/usage.png)

_Examples of generated diagrams can be found in the [examples](examples) directory._

## 🤔 How it Works

1. ℹ️ It connects, by using the official [Apache Airflow Python Client](https://github.com/apache/airflow-client-python), to your Airflow installation to retrieve all DAGs (in case you don't specify any `dag_id`) and all Tasks for the DAG(s).
1. 🪄 It processes every DAG and its Tasks and 🔮 tries to find a diagram node for every DAGs task, by using [Fuzzy String Matching](https://github.com/seatgeek/thefuzz), that matches the most. If you are unhappy about the match you can also provide a `mapping.yml` file to statically map from Airflow task to diagram node.
1. 🎨 It renders the results into a python file which can then be executed to retrieve the rendered diagram. 🎉

## ❤️ Contributing

Contributions are very welcome. Please go ahead and raise an issue if you have one or open a PR. Thank you.
