from diagrams import Diagram
from diagrams.k8s.compute import Pod

with Diagram("dbt", show=False):
    dbt_run = Pod("dbt_run")
    
    