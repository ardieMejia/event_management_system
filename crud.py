import unittest
import pandas as pd
from tabulate import tabulate
import random
import os
import sys

class Crud:
    def __init__(self):
        pass

    def Input_error_message(*args):
        len_char = len(*args)
        print('+' * len_char)
        print(*args)
        print('+' * len_char + '\n')

    
    # Menu Read
    def Show_specific_data(self,model):
        ask_input_ID = input('Input ' + model.id_field + ': ').upper().strip()
        
        if ask_input_ID in model.data[model.id_field].values:
            print(tabulate(model.data.loc[model.data[model.id_field] == ask_input_ID].values, headers= model.data.columns, tablefmt='fancy_grid'))
        else:
            print(model.id_field + ' not found')
            
            while True:
                find_other_ID = input('Search other ID [Y/N]:').upper().strip()
                print()
                if find_other_ID == 'Y':
                    Show_specific_data(model.data, model.id_field)
                elif find_other_ID == 'N':
                    break
                else:
                    self.Input_error_message('Invalid Input. Input "Y" to search other ID or "N" to exit')
            

    def ID_generator(self,model):
        # DEPARTMENT_initial = ''.join([word[0].upper() for word in department.split()])      
        
        # residence_initial = ''.join([word[0].upper() for word in residence.split()])   
        # name_length = len(name.strip())
        # id_generator = f'{DEPARTMENT_initial}{gender}{residence_initial}{name_length}'
        
        id_generator = random.randint(10000,99999)
        
        
        all_ids = model.data['MEMBER ID'].tolist() + model.usedID_data['MEMBER ID'].tolist()           
        while id_generator in all_ids:
            # name_length += 1
            # id_generator = f'{DEPARTMENT_initial}{gender}{residence_initial}{name_length}'
            id_generator = random.randint(10000,99999)
            
        model.temporary_value.update({model.id_field: id_generator})


        return id_generator



    # Menu Create
    def Input_data_member(self,model, parent_model):
        # global members_path, used_membersID_path
        while True:
            column_input_NAME = 'NAME'
            input_NAME = input('NAME: ').title().strip()
            
            if self.Input_member_checker(input_NAME, column_input_NAME, parent_model) == True:
                model.temporary_value.update({'NAME': input_NAME})
                break
            else:
                continue
            
        while True:
            column_input_CONTACT_NUMBER = 'CONTACT NUMBER'
            input_CONTACT_NUMBER = input('CONTACT NUMBER: ').title()   
            
            if self.Input_member_checker(input_CONTACT_NUMBER, column_input_CONTACT_NUMBER, parent_model) == True:
                model.temporary_value.update({'CONTACT NUMBER': input_CONTACT_NUMBER})
                break
            else:
                continue
                
        while True:
            column_input_EMAIL_ADDRESS = 'EMAIL ADDRESS'
            input_EMAIL_ADDRESS = input('EMAIL ADDRESS: ').upper().strip()
            
            if self.Input_member_checker(input_EMAIL_ADDRESS, column_input_EMAIL_ADDRESS, parent_model) == True:
                model.temporary_value.update({'EMAIL ADDRESS': input_EMAIL_ADDRESS})
                break
            else:
                continue
                    
        while True:
            column_input_EVENT = 'EVENT ID'
            print(tabulate(parent_model.data, headers='keys', tablefmt='fancy_grid'))
            
            input_EVENT_ID = input('EVENT ID: ').title().strip()
            if self.Input_member_checker(input_EVENT_ID, column_input_EVENT, parent_model) == True:
                model.temporary_value.update({'EVENT ID': input_EVENT_ID})
                break
            else:
                continue  

            
        generated_id = self.ID_generator(model)
                        
        while True:
            input_confirmation_add_data = input(f"Are you sure you want to add data with Member ID {model.temporary_value['MEMBER ID']}? [Y/N]: ").upper().strip()
            print()
            if input_confirmation_add_data == 'Y':
                model.data = pd.concat([model.data, pd.DataFrame.from_dict(model.temporary_value, orient= 'index').T], ignore_index= True)
                
                print('\nData Saved')
                model.data = model.data.astype(str)
                model.data.to_excel(model.path, index=False)
                    
                model.usedID_data.loc[len(model.usedID_data)] = generated_id
                model.usedID_data.to_excel(model.usedID_path, index= False)
                print(tabulate(model.data, headers='keys', tablefmt='fancy_grid'))
                break
            elif input_confirmation_add_data == 'N':
                break
            else:
                self.Input_error_message('Invalid input. Input [Y] to proceed or [N] to cancel')
                    


    def Input_member_checker(self,input, column, parent_model):

        if column == 'NAME':  
            check_character_NAME = ''.join(input.split())   
            if check_character_NAME.isalpha():  
                return True
            else:
                print('NAME can only be filled with letters')
                return False
        
        elif column == 'CONTACT NUMBER':
            if not input.isnumeric():     
                print('Contact number must be numeric')
                return False
            else:
                return True
        
        elif column == 'EMAIL ADDRESS':
            if "@" in input:
                return True
            else:
                print("Please enter a valid email address")
                return False
        
        elif column == 'EVENT ID':
            for i in parent_model.data['EVENT ID'].values:
                if input in parent_model.data['EVENT ID'].values:
                    return True
                else:
                    print('Please enter a valid department name')
                    return False




    # Menu Delete
    def Delete_data(self,model):
        input_id_delete = input(model.id_field + ': ').upper().strip()       
        
        if input_id_delete not in model.data[model.id_field].values:
            self.Input_error_message(f'{input_id_delete} does not exist')
            return
        
        index_to_delete = model.data.loc[model.data[model.id_field] == input_id_delete].index         
        print(tabulate(model.data.loc[model.data[model.id_field] == input_id_delete], headers= model.data.columns, tablefmt='fancy_grid'))
        
        while True:
            input_confirmation_delete_data = input(f"Are you sure you want to delete data with ID {model.data.loc[index_to_delete, model.id_field].values}? [Y/N]: ").upper().strip()
            if input_confirmation_delete_data == 'Y':
                model.data = model.data.drop(index_to_delete)            
                model.data.to_excel(model.path, index=False)            
                print('\nData has been successfully deleted\n')
                index_to_delete = model.usedID_data.loc[model.usedID_data[model.id_field] == input_id_delete].index         
                model.usedID_data = model.usedID_data.drop(index_to_delete)
                model.usedID_data.to_excel(model.usedID_path, index=False)            
                print('\nused ID cleaned\n')
                break
            
            elif input_confirmation_delete_data == 'N':
                print('\nThe deletion process has been canceled\n')
                break
            
            else:
                self.Input_error_message('Invalid input. Input [Y] to proceed or [N] to cancel')
                continue
            

    # Menu Update
    def Update_data(self,model, index_change, column_change, value): 
        while True:
            input_update_data_confirmation = input(f"Are you sure you want to update this value for ID {model.data.loc[index_change][model.id_field].values}? [Y/N]: ").upper().strip()
            if input_update_data_confirmation == 'Y':
                model.data.loc[index_change, column_change] = value      
                model.data.to_excel(model.path, index=False)
                print(tabulate(model.data.loc[index_change, :], headers='keys', tablefmt='fancy_grid'))
                break
            
            elif input_update_data_confirmation == 'N':
                print('\nThe update process has been canceled.\n')
                break
            
            else:
                self.Input_error_message('Invalid Input. Input [Y] to proceed or [N] to cancel')

                
    def Input_data_to_change(self,model, parent_model):
        while True:
            input_id_update = input(model.id_field + ': ').upper().strip()
            
            if input_id_update in model.data[model.id_field].values:
                print(tabulate(model.data.loc[model.data[model.id_field] == input_id_update].values, headers= model.data.columns, tablefmt='fancy_grid'))
                index_to_update = model.data.loc[model.data[model.id_field] == input_id_update].index
                
            else:
                self.Input_error_message(f'There is no Member with ID: {input_id_update}')
                break
        
            column_to_update = None                   
            while True:                
                input_confirmation_change_data = input('Input [Y] to proceed or [N] to cancel: ').upper().strip()


                if input_confirmation_change_data == 'Y':
                    while True:
                        input_column_change = input('Please enter the column name: ').upper().strip()
                    
                        if input_column_change in model.data.columns:      
                            column_to_update = input_column_change
                            break

                        else:
                            self.Input_error_message(f'Column {input_column_change} does not exist')
                            continue
                    
                    if column_to_update == 'NAME':
                        while True:
                            input_new_NAME = input(f'Input new {input_column_change}: ').title().strip()
                            
                            if self.Input_member_checker(input_new_NAME, column_to_update,parent_model) == True:
                                self.Update_data(model, index_change= index_to_update, column_change= column_to_update, value= input_new_NAME)
                                return
                            else:
                                continue

                    elif column_to_update == 'CONTACT NUMBER':
                        while True:
                            input_new_CONTACT_NUMBER = input(f'Input new {input_column_change}: ').title()
                            
                            if self.Input_member_checker(input_new_CONTACT_NUMBER, column_to_update,parent_model) == True:
                                self.Update_data(model, index_change= index_to_update, column_change= column_to_update, value= input_new_CONTACT_NUMBER.strip())
                                return
                            else:
                                continue

                    elif column_to_update == 'EMAIL ADDRESS':
                        while True:
                            input_new_EMAIL_ADDRESS = input(f'Input new {input_column_change}: ').upper().strip()
                            
                            if self.Input_member_checker(input_new_EMAIL_ADDRESS, column_to_update,parent_model) == True:
                                self.Update_data(model, index_change= index_to_update, column_change= column_to_update, value= input_new_EMAIL_ADDRESS)
                                return
                            else:
                                continue
                    
                    elif column_to_update == 'EVENT ID':
                        while True:
                            print(tabulate(event_data, headers='keys', tablefmt='fancy_grid'))
                            
                            input_new_EVENT_ID = input(f'Input new {input_column_change}: ').title().strip()
                            
                            if self.Input_member_checker(input_new_EVENT_ID, column_to_update,parent_model) == True:
                                self.Update_data(model, index_change= index_to_update, column_change= column_to_update, value= input_new_EVENT_ID)
                                return
                            else:
                                continue

                    elif input_column_change == 'MEMBER ID':
                        self.Input_error_message('Can not change MEMBER ID')
                        return
                
                elif input_confirmation_change_data == 'N':
                    return
                else:
                    self.Input_error_message('Invalid input. Input [Y] to proceed or [N] to cancel')
                    
