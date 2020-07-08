import setuptools

with open("version.txt", "r") as fh:
    version = fh.read()

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="airflow-diagrams",
    version=version,
    author="Felix Uellendall",
    author_email="feluelle@pm.me",
    description="Auto-generated Diagrams from Airflow DAGs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/feluelle/airflow-diagrams",
    install_requires=[
        'apache-airflow',
        'diagrams'
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
