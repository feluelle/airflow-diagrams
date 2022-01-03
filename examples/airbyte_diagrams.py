from diagrams import Diagram
from diagrams.generic.blank import Blank

with Diagram("airbyte", show=False):
    airbyte_job_sensor = Blank("airbyte_job_sensor")
    airbyte_trigger_async = Blank("airbyte_trigger_async")
    
    airbyte_trigger_async >> [airbyte_job_sensor]