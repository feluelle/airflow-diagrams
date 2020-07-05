"""
Helper script to output available diagram nodes.
"""
import ast
import json
import os

import diagrams


def find_nodes(directory_name):
    _nodes = []
    for root, _, files in os.walk(os.path.dirname(directory_name)):
        for file in files:
            if not file.endswith('.py') or file == '__init__.py':
                continue
            file_path = os.path.join(root, file)
            _, provider, resource_type = file_path.replace('.py', '').rsplit('/', 2)
            with open(file_path) as f_open:
                node = ast.parse(f_open.read())
            for node in ast.walk(node):
                if isinstance(node, ast.ClassDef) and not node.name.startswith('_'):
                    _nodes.append(dict(provider=provider, resource_type=resource_type, name=node.name))
    return _nodes


all_nodes = (
    find_nodes(diagrams.__file__)
)

with open('diagrams_nodes.json', 'w') as json_file:
    json.dump(all_nodes, json_file)
