# airflow-diagrams

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/feluelle/airflow-diagrams/master.svg)](https://results.pre-commit.ci/latest/github/feluelle/airflow-diagrams/master)
[![PyPI version](https://img.shields.io/pypi/v/airflow-diagrams)](https://pypi.org/project/airflow-diagrams/)
[![License](https://img.shields.io/pypi/l/airflow-diagrams)](https://github.com/feluelle/airflow-diagrams/blob/master/LICENSE)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/airflow-diagrams)](https://pypi.org/project/airflow-diagrams/)

> Auto-generated Diagrams from Airflow DAGs.

This project aims to easily visualise your [Airflow](https://github.com/apache/airflow) DAGs on service level
from providers like AWS, GCP, Azure, etc. via [diagrams](https://github.com/mingrammer/diagrams).

## 🚀 Get started

To install it from [PyPI](https://pypi.org/) run:
```
pip install airflow-diagrams
```
Then just call it like this:
```
Usage: airflow-diagrams generate [OPTIONS]

  Generates <airflow-dag-id>_diagrams.py in <output-path> directory which
  contains the definition to create a diagram. Run this file and you will get
  a rendered diagram.

Options:
  -d, --airflow-dag-id TEXT    The dag id from which to generate the diagram.
                               By default it generates for all.
  -h, --airflow-host TEXT      The host of the airflow rest api from where to
                               retrieve the dag tasks information.  [default:
                               http://localhost:8080/api/v1]
  -u, --airflow-username TEXT  The username of the airflow rest api.
                               [default: admin]
  -p, --airflow-password TEXT  The password of the airflow rest api.
                               [default: admin]
  -o, --output-path DIRECTORY  The path to output the diagrams to.  [default:
                               .]
  -m, --mapping-file FILE      The mapping file to use for static mapping from
                               Airflow task to diagram node. By default no
                               mapping file is being used.
  -v, --verbose                Verbose output i.e. useful for debugging
                               purposes.
  --help                       Show this message and exit.
```
_Examples of generated diagrams can be found in the [examples](examples) directory._

## 🤔 How it Works

ℹ️ At first it connects, by using the official [Apache Airflow Python Client](https://github.com/apache/airflow-client-python), to your Airflow installation to retrieve all DAGs (in case you don't specify any `dag_id`) and all Tasks for the DAG(s).

🔮 Then it tries to find a diagram node for every DAGs task, by using [Fuzzy String Matching](https://github.com/seatgeek/thefuzz), that matches the most. If you are unhappy about the match you can also provide a `mapping.yml` file to statically map from Airflow task to diagram node.

🪄 Lastly it renders the results into a python file which can then be executed to retrieve the rendered diagram. 🎉

## ❤️ Contributing

Contributions are very welcome. Please go ahead and raise an issue if you have one or open a PR. Thank you.
