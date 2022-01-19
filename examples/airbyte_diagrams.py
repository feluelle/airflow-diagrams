from diagrams import Diagram
from diagrams.generic.blank import Blank

with Diagram("airbyte", show=False):
    _6779f45be4c8a58feed5ddfda70e2382 = Blank("airbyte_job_sensor")
    _30e82bea0c5181aad98d772e9133b66b = Blank("airbyte_trigger_async")
    
    _30e82bea0c5181aad98d772e9133b66b >> [_6779f45be4c8a58feed5ddfda70e2382]
    