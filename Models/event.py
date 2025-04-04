import pandas as pd
import os
import sys



class Event:
    def __init__(self,path, usedID_path, id_field):
        self.path = path
        self.usedID_path = usedID_path
        self.id_field = id_field
        print("created event with path of ", self.path)
        print("used ID is stored at ", self.usedID_path)
        self.data = pd.read_excel(self.path, dtype= 'str')
        self.usedID_data = pd.read_excel(self.usedID_path, dtype= 'str')

        
        self.temporary_value = {         # This variable is used for storing our input when using menu create and update
            'EVENT ID': [], 
            'EVENT NAME': [], 
            'EVENT DATE': [],
            'EVENT FORMAT': [],
            'NUMBER OF ROUNDS': [],
            'GENDER': [],
            'CATEGORY': [],
            'SUB CATEGORY': [],            
            'COST': []
        }


        
        # print(os.path.realpath(__file__))

                        


