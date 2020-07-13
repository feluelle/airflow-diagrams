"""
Helper script to create dictionary keys for all available operators of current installed airflow package.
"""
import json

with open('airflow_operators.json', 'r') as json_file:
    all_operators = json.load(json_file)

with open('../../airflow_diagrams/mapping.json', 'r') as json_file:
    existing_operators = json.load(json_file)

for operator in all_operators:
    existing_operators.setdefault(operator, dict(provider='generic', resource_type='blank', name='Blank'))
existing_operators = dict(sorted(existing_operators.items()))

with open('../../airflow_diagrams/mapping.json', 'w') as json_file:
    json.dump(existing_operators, json_file)
