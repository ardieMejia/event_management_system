import unittest
import pandas as pd
from tabulate import tabulate
import random
import Event as Event
import Global as Global
import Member as Member

# Global Variable and Function
temporary_members_value = {         # These 2 variables is used for storing our input when using menu create and update
    'MEMBER ID': [], 
    'NAME': [],
    'CONTACT NUMBER': [],
    'EMAIL ADDRESS': [],
    'EVENT ID': []
}


temporary_events_value= {
    'EVENT ID': [], 
    'EVENT DATE': [],
    'EVENT FORMAT': [],
    'NUMBER OF ROUNDS': [],
    'COST': []
}






        
Member.Main_flow()
