from diagrams import Diagram
from diagrams.generic.blank import Blank

with Diagram("mails_to_postgres", show=False):
    transfer_imap_mails_to_s3 = Blank("transfer_imap_mails_to_s3")
    
    
    