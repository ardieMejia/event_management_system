import unittest
import pandas as pd
from tabulate import tabulate
import random
import os
import sys
import pandas as pd



# Global Variable and Function



class Event:
    def __init__(self, path, usedID_path):
        print("created event")
        self.path = path
        self.usedID_path = usedID_path
                



        # self.id_field = id_field
        # print("created member with path of ", self.path)
        print("used ID is stored at ", self.usedID_path)
        self.data = pd.read_excel(self.path, dtype= 'str')
        self.usedID_data = pd.read_excel(self.usedID_path, dtype= 'str')
        
        
        self.temporary_value = {         # This variable is used for storing our input when using menu create and update
            'EVENT ID': [], 
            'EVENT DATE': [],
            'EVENT FORMAT': [],
            'NUMBER OF ROUNDS': [],
            'COST': []
        }

        




class Member:
    def __init__(self, path, usedID_path):
        print("created member")
        self.path = path
        self.usedID_path = usedID_path
                



        # self.id_field = id_field
        # print("created member with path of ", self.path)
        print("used ID is stored at ", self.usedID_path)
        self.data = pd.read_excel(self.path, dtype= 'str')
        self.usedID_data = pd.read_excel(self.usedID_path, dtype= 'str')
        
        self.temporary_value = {         # This variable is used for storing our input when using menu create and update
            'MEMBER ID': [],
            'NAME': [],
            'CONTACT NUMBER': [],
            'EMAIL ADDRESS': [],
            'EVENT ID': []
        }

    def test(self):
        return "hahahha spider"


        
                        




class Crud:
    def __init__(self):
        pass


    def ID_generator(self,model):        
        id_generator = random.randint(10000,99999)
        
        # ========== later should replace this with model.data[model.id_field]
        all_ids = model.data['MEMBER ID'].tolist() + model.usedID_data['MEMBER ID'].tolist()           
        while id_generator in all_ids:
            # name_length += 1
            # id_generator = f'{DEPARTMENT_initial}{gender}{residence_initial}{name_length}'
            id_generator = random.randint(10000,99999)
            
        model.temporary_value.update({model.id_field: id_generator})


        return id_generator

 
    # Menu Create
    def Input_data_member(self, member):
                
        # global members_path, used_membersID_path
        
        # input_NAME = input('NAME: ').title().strip()
        generated_id = self.ID_generator(member)
        
        member.temporary_value['MEMBER ID'] = generated_id
        member.temporary_value['NAME'] = member.temporary_value['NAME'].title().strip()
        member.temporary_value['CONTACT NUMBER'] = member.temporary_value['CONTACT NUMBER'].title()
        member.temporary_value['EMAIL ADDRESS'] = member.temporary_value['EMAIL ADDRESS'].upper().strip()
        member.temporary_value['EVENT ID'] = member.temporary_value['EVENT ID'].title().strip()
        # input_EMAIL_ADDRESS = input('EMAIL ADDRESS: ').upper().strip()
        # input_EVENT_ID = input('EVENT ID: ').title().strip()



    

        # if self.Input_member_checker(input_NAME, column_input_NAME, parent_model) == True:
        # self.Input_member_checker(input_EVENT_ID, column_input_EVENT, parent_model) == True:
        
        # member.temporary_value.update({'NAME': input_NAME}).title().strip()
        #                 model.temporary_value.update({'CONTACT NUMBER': input_CONTACT_NUMBER})
        #                                 model.temporary_value.update({'EMAIL ADDRESS': input_EMAIL_ADDRESS})
        #                                                 model.temporary_value.update({'EVENT ID': input_EVENT_ID})



        
        
        member.data = pd.concat([member.data, pd.DataFrame.from_dict(member.temporary_value, orient= 'index').T], ignore_index= True)
        
        member.data = member.data.astype(str)
        member.data.to_excel(member.path, index=False)
        




            
                        


