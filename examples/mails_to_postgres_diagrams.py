from diagrams import Diagram
from diagrams.aws.storage import SimpleStorageServiceS3

with Diagram("mails_to_postgres", show=False):
    _5b3a2bc96456974068c7fdf8560d2e4e = SimpleStorageServiceS3("transfer_imap_mails_to_s3")
    
    