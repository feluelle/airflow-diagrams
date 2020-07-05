"""
Helper script to output available airflow operators.
"""
import ast
import json
import os

from airflow import operators, sensors
from airflow.contrib import operators as contrib_operators, sensors as contrib_sensors


def _find_operators(directory_name):
    _operators = []
    for root, _, files in os.walk(os.path.dirname(directory_name)):
        for file in files:
            if not file.endswith('.py') or file == '__init__.py':
                continue
            file_path = os.path.join(root, file)
            with open(file_path) as f_open:
                node = ast.parse(f_open.read())
            for node in ast.walk(node):
                if isinstance(node, ast.ClassDef) and (
                        node.name.endswith('Operator') or node.name.endswith('Sensor')
                ):
                    _operators.append(node.name)
    return _operators


all_operators = (
        _find_operators(operators.__file__) +
        _find_operators(contrib_operators.__file__) +
        _find_operators(sensors.__file__) +
        _find_operators(contrib_sensors.__file__)
)

with open('airflow_operators.json', 'w') as json_file:
    json.dump(all_operators, json_file)
