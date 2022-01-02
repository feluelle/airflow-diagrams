import setuptools

from airflow_diagrams import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="airflow-diagrams",
    version=__version__,
    author="Felix Uellendall",
    author_email="feluelle@pm.me",
    description="Auto-generated Diagrams from Airflow DAGs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/feluelle/airflow-diagrams",
    install_requires=[
        "typer==0.4.0",
        "requests==2.26.0",
        "diagrams==0.20.0",
        "thefuzz[speedup]==0.19.0",
        "jinja2<3.0,>=2.10",
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
