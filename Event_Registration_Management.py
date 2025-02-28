import unittest
import pandas as pd
from tabulate import tabulate
import random
from Models.member import Member 
from Models.event import Event





member = Member(r"./Members_Data.xlsx", r'./Used_MembersID.xlsx', "MEMBER ID")
event = Event(r"./Events_Data.xlsx", r'./Used_EventsID.xlsx', "EVENT ID") 




def Call_menu(menus, menu_title):
    print('----------------------------')
    print("{:^29}".format(menu_title))
    print('----------------------------')
    for i, option in enumerate(menus, start=1):
        print(f"{i}. {option}")
        print('----------------------------')
    input_menu = input('Select Menu: ').strip()
    return input_menu


def Menu_error_message(*args):
    print('Menu', *args, 'does not exist\n')

def ID_generator(name, contact_number, email_address, event_id):
    # DEPARTMENT_initial = ''.join([word[0].upper() for word in department.split()])      
                                                                                        
    # residence_initial = ''.join([word[0].upper() for word in residence.split()])   
    # name_length = len(name.strip())
    # id_generator = f'{DEPARTMENT_initial}{gender}{residence_initial}{name_length}'

    id_generator = random.randint(10000,99999)


    all_ids = member.data['MEMBER ID'].tolist() + member.usedID_data['MEMBER ID'].tolist()           
    while id_generator in all_ids:
        # name_length += 1
        # id_generator = f'{DEPARTMENT_initial}{gender}{residence_initial}{name_length}'
        id_generator = random.randint(10000,99999)
    
    member.temporary_value.update({'MEMBER ID': id_generator})
    return id_generator

    
# Menu Read
def Show_specific_data(): 
    ask_input_ID = input('Input ' + member.id_field + ': ').upper().strip()

    if ask_input_ID in member.data[member.id_field].values:
        print(tabulate(member.data.loc[member.data[member.id_field] == ask_input_ID].values, headers= member.data.columns, tablefmt='fancy_grid'))
    else:
        print(member.id_field + ' not found')
        
    while True:
        find_other_ID = input('Search other ID [Y/N]:').upper().strip()
        print()
        if find_other_ID == 'Y':
            Show_specific_data(member.data, member.id_field)
        elif find_other_ID == 'N':
            break
        else:
            Input_error_message('Invalid Input. Input "Y" to search other ID or "N" to exit')

def Input_member_checker(input, column):

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
        for i in event.data['EVENT ID'].values:
            print(i)
            print(type(i))
        if input in event.data['EVENT ID'].values:
            return True
        else:
            print('Please enter a valid department name')
            return False



        
# Menu Create
def Input_data_member():
    # global members_path, used_membersID_path
    while True:
        column_input_NAME = 'NAME'
        input_NAME = input('NAME: ').title().strip()
        
        if Input_member_checker(input_NAME, column_input_NAME) == True:
            member.temporary_value.update({'NAME': input_NAME})
            break
        else:
            continue

    while True:
        column_input_CONTACT_NUMBER = 'CONTACT NUMBER'
        input_CONTACT_NUMBER = input('CONTACT NUMBER: ').title()   
        
        if Input_member_checker(input_CONTACT_NUMBER, column_input_CONTACT_NUMBER) == True:
            member.temporary_value.update({'CONTACT NUMBER': input_CONTACT_NUMBER})
            break
        else:
            continue

    while True:
        column_input_EMAIL_ADDRESS = 'EMAIL ADDRESS'
        input_EMAIL_ADDRESS = input('EMAIL ADDRESS: ').upper().strip()

        if Input_member_checker(input_EMAIL_ADDRESS, column_input_EMAIL_ADDRESS) == True:
            member.temporary_value.update({'EMAIL ADDRESS': input_EMAIL_ADDRESS})
            break
        else:
            continue

    while True:
        column_input_EVENT = 'EVENT ID'
        print(tabulate(event.data, headers='keys', tablefmt='fancy_grid'))

        input_EVENT_ID = input('EVENT ID: ').title().strip()
        if Input_member_checker(input_EVENT_ID, column_input_EVENT) == True:
            member.temporary_value.update({'EVENT ID': input_EVENT_ID})
            break
        else:
            continue  
    generated_id = ID_generator(name= input_NAME, contact_number= input_CONTACT_NUMBER, email_address= input_EMAIL_ADDRESS, event_id= input_EVENT_ID)
        
    while True:
        input_confirmation_add_data = input(f"Are you sure you want to add data with Member ID {member.temporary_value['MEMBER ID']}? [Y/N]: ").upper().strip()
        print()
        if input_confirmation_add_data == 'Y':
            member.data = pd.concat([member.data, pd.DataFrame.from_dict(member.temporary_value, orient= 'index').T], ignore_index= True)
            
            print('\nData Saved')
            member.data = member.data.astype(str)
            member.data.to_excel(member.path, index=False)

            member.usedID_data.loc[len(member.usedID_data)] = generated_id
            member.usedID_data.to_excel(member.usedID_path, index= False)
            print(tabulate(member.data, headers='keys', tablefmt='fancy_grid'))
            break
        elif input_confirmation_add_data == 'N':
            break
        else:
            Input_error_message('Invalid input. Input [Y] to proceed or [N] to cancel')


def Input_data_to_change():
    while True:
        input_id_update = input(member.id_field + ': ').upper().strip()   

        if input_id_update in member.data[member.id_field].values:
            print(tabulate(member.data.loc[member.data[member.id_field] == input_id_update].values, headers= member.data.columns, tablefmt='fancy_grid'))
            index_to_update = member.data.loc[member.data[member.id_field] == input_id_update].index
            
        else:
            Input_error_message(f'There is no Member with ID: {input_id_update}')
            break
        
        column_to_update = None                   
        while True:                
            input_confirmation_change_data = input('Input [Y] to proceed or [N] to cancel: ').upper().strip()


            if input_confirmation_change_data == 'Y':
                while True:
                    input_column_change = input('Please enter the column name: ').upper().strip()
                    
                    if input_column_change in member.data.columns:      
                        column_to_update = input_column_change
                        break

                    else:
                        Input_error_message(f'Column {input_column_change} does not exist')
                        continue
                    
                if column_to_update == 'NAME':
                    while True:
                        input_new_NAME = input(f'Input new {input_column_change}: ').title().strip()

                        if Input_member_checker(input_new_NAME, column_to_update) == True:
                            Update_data(index_change= index_to_update, column_change= column_to_update, value= input_new_NAME)
                            return
                        else:
                            continue

                elif column_to_update == 'CONTACT NUMBER':
                    while True:
                        input_new_CONTACT_NUMBER = input(f'Input new {input_column_change}: ').title()

                        if Input_member_checker(input_new_CONTACT_NUMBER, column_to_update) == True:
                            Update_data(index_change= index_to_update, column_change= column_to_update, value= input_new_CONTACT_NUMBER.strip())
                            return
                        else:
                            continue

                elif column_to_update == 'EMAIL ADDRESS':
                    while True:
                        input_new_EMAIL_ADDRESS = input(f'Input new {input_column_change}: ').upper().strip()

                        if Input_member_checker(input_new_EMAIL_ADDRESS, column_to_update) == True:
                            Update_data(index_change= index_to_update, column_change= column_to_update, value= input_new_EMAIL_ADDRESS)
                            return
                        else:
                            continue

                elif column_to_update == 'EVENT ID':
                    while True:
                        print(tabulate(event_data, headers='keys', tablefmt='fancy_grid'))

                        input_new_EVENT_ID = input(f'Input new {input_column_change}: ').title().strip()

                        if Input_member_checker(input_new_EVENT_ID, column_to_update) == True:
                            Update_data(index_change= index_to_update, column_change= column_to_update, value= input_new_EVENT_ID)
                            return
                        else:
                            continue

                elif input_column_change == 'MEMBER ID':
                    Input_error_message('Can not change MEMBER ID')
                    return
                
            elif input_confirmation_change_data == 'N':
                return
            else:
                Input_error_message('Invalid input. Input [Y] to proceed or [N] to cancel')


                
# Menu Update
def Update_data(index_change, column_change, value): 
    while True:
        input_update_data_confirmation = input(f"Are you sure you want to update this value for ID {member.data.loc[index_change]['MEMBER ID'].values}? [Y/N]: ").upper().strip()
        if input_update_data_confirmation == 'Y':
            member.data.loc[index_change, column_change] = value      
            member.data.to_excel(member.path, index=False)
            print(tabulate(member.data.loc[index_change, :], headers='keys', tablefmt='fancy_grid'))
            break
        
        elif input_update_data_confirmation == 'N':
            print('\nThe update process has been canceled.\n')
            break

        else:
            Input_error_message('Invalid Input. Input [Y] to proceed or [N] to cancel')


            
# Menu Delete
def Delete_data():
    input_id_delete = input(member.id_field + ': ').upper().strip()       
    
    if input_id_delete not in member.data[member.id_field].values:
        Input_error_message(f'{input_id_delete} does not exist')
        return
    
    index_to_delete = member.data.loc[member.data[member.id_field] == input_id_delete].index         
    print(tabulate(member.data.loc[member.data[member.id_field] == input_id_delete], headers= member.data.columns, tablefmt='fancy_grid'))

    while True:
        input_confirmation_delete_data = input(f"Are you sure you want to delete data with ID {member.data.loc[index_to_delete, member.id_field].values}? [Y/N]: ").upper().strip()
        if input_confirmation_delete_data == 'Y':
            member.data = member.data.drop(index_to_delete)
            member.data.to_excel(member.path, index=False)
            print('\nData has been successfully deleted\n')
            break

        elif input_confirmation_delete_data == 'N':
            print('\nThe deletion process has been canceled\n')
            break
        
        else:
            Input_error_message('Invalid input. Input [Y] to proceed or [N] to cancel')
            continue
            
            
def Main_flow():

    #     # Define DF

    
    print("done")


    while True:
        main_menu_input = Call_menu(['Members Data', 'Add Data', 'Change Data', 'Delete Data', 'Exit'], menu_title= 'Main Menu')
        if main_menu_input == '1':      # Menu Read
            while True:
                sub_menu_1_input = Call_menu(['Show All Data', 'Search ID', 'Main Menu'], menu_title= 'Employee Data')
                if sub_menu_1_input == '1':     # Show all members data
                    print("show")
                    member.data = member.data.astype(str)
                    print(tabulate(member.data, headers='keys', tablefmt='fancy_grid', floatfmt='14.0f'))
                elif sub_menu_1_input == '2':   # Show specific data based on ID
                    Show_specific_data()
                elif sub_menu_1_input == '3':   # Return to main menu
                    break
                else:
                    Menu_error_message(sub_menu_1_input)

                
        elif main_menu_input == '2':    # Menu Create
            while True:
                sub_menu_2_input = Call_menu(['Add Member Data', 'Main Menu'], menu_title= 'Add Data')
                if sub_menu_2_input == '1':     # Add new member
                    Input_data_member()
                elif sub_menu_2_input == '2':   # Return to main menu
                    break
                else:
                    Menu_error_message(sub_menu_2_input)
                    
        elif main_menu_input == '3':    # Menu Update
            while True:
                sub_menu_3_input = Call_menu(['Change Member Data', 'Main Menu'], menu_title= 'Change Data')
                if sub_menu_3_input == '1':     # Change member data based on ID
                    Input_data_to_change()
                elif sub_menu_3_input == '2':   # Return to main menu
                    break
                else:
                    Menu_error_message(sub_menu_3_input)
                    

        elif main_menu_input == '4':    # Menu Delete
            while True:
                sub_menu_4_input = Call_menu(['Delete Member Data', 'Main Menu'], menu_title= 'Delete Data')
                if sub_menu_4_input == '1':     # Delete employee data based on ID
                    Delete_data()
                elif sub_menu_4_input == '2':   # Return to main menu
                    break
                else:
                    Menu_error_message(sub_menu_4_input)
                    
        elif main_menu_input == '5':    
            exit()
        else:
            Menu_error_message(main_menu_input)
            


        
Main_flow()
