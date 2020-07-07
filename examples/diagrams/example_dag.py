from diagrams import Diagram
from diagrams.generic.blank import Blank

with Diagram("example_dag", show=False):
    run_this_1 = Blank("run_this_1")
    run_this_2a = Blank("run_this_2a")
    run_this_3 = Blank("run_this_3")
    run_this_2b = Blank("run_this_2b")
    
    run_this_1 >> run_this_2a
    run_this_2a >> run_this_3
    run_this_1 >> run_this_2b
    run_this_2b >> run_this_3
    