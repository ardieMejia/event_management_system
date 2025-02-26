import unittest
import pandas as pd
from tabulate import tabulate
import random


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

def Input_error_message(*args):
    len_char = len(*args)
    print('+' * len_char)
    print(*args)
    print('+' * len_char + '\n')

def Input_member_checker(input, column, evt):

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
        for i in evt['EVENT ID'].values:
            print(i)
            print(type(i))
        if input in evt['EVENT ID'].values:
            return True
        else:
            print('Please enter a valid department name')
            return False
        

    
def ID_generator(data, used_id, name, contact_number, email_address, event_id):
    global temporary_members_value
    # DEPARTMENT_initial = ''.join([word[0].upper() for word in department.split()])      
                                                                                        
    # residence_initial = ''.join([word[0].upper() for word in residence.split()])   
    # name_length = len(name.strip())
    # id_generator = f'{DEPARTMENT_initial}{gender}{residence_initial}{name_length}'

    id_generator = random.randint(10000,99999)


    # all_ids = data['EMPLOYEE ID'].tolist() + used_id['EMPLOYEE ID'].tolist()           
    # while id_generator in all_ids:
    #     name_length += 1
    #     id_generator = f'{DEPARTMENT_initial}{gender}{residence_initial}{name_length}'
    
    temporary_members_value.update({'MEMBER ID': id_generator})
    return id_generator

# Menu Read
def Show_specific_data(data): 
    ask_input_ID = input('Input MEMBER ID: ').upper().strip()

    if ask_input_ID in data["MEMBER ID"].values:
        print(tabulate(data.loc[data['MEMBER ID'] == ask_input_ID].values, headers= data.columns, tablefmt='fancy_grid'))
    else:
        print('MEMBER ID not found')
        
    while True:
        find_other_ID = input('Search other ID [Y/N]:').upper().strip()
        print()
        if find_other_ID == 'Y':
            Show_specific_data(data)
        elif find_other_ID == 'N':
            break
        else:
            Input_error_message('Invalid Input. Input "Y" to search other ID or "N" to exit')

# Menu Create
def Input_data_member(data, used_id, evt, value):
    global members_path, used_membersID_path
    while True:
        column_input_NAME = 'NAME'      
        input_NAME = input('NAME: ').title().strip()
        
        if Input_member_checker(input_NAME, column_input_NAME, evt= evt) == True:
            value.update({'NAME': input_NAME})
            break
        else:
            continue

    while True:
        column_input_CONTACT_NUMBER = 'CONTACT NUMBER'
        input_CONTACT_NUMBER = input('CONTACT NUMBER: ').title()   
        
        if Input_member_checker(input_CONTACT_NUMBER, column_input_CONTACT_NUMBER, evt= evt) == True:
            value.update({'CONTACT NUMBER': input_CONTACT_NUMBER})
            break
        else:
            continue

    while True:
        column_input_EMAIL_ADDRESS = 'EMAIL ADDRESS'
        input_EMAIL_ADDRESS = input('EMAIL ADDRESS: ').upper().strip()

        if Input_member_checker(input_EMAIL_ADDRESS, column_input_EMAIL_ADDRESS, evt= evt) == True:
            value.update({'EMAIL ADDRESS': input_EMAIL_ADDRESS})
            break
        else:
            continue

    while True:
        column_input_EVENT = 'EVENT ID'
        print(tabulate(evt, headers='keys', tablefmt='fancy_grid'))

        input_EVENT_ID = input('EVENT ID: ').title().strip()
        if Input_member_checker(input_EVENT_ID, column_input_EVENT, evt= evt) == True:
            value.update({'EVENT ID': input_EVENT_ID})
            break
        else:
            continue  
    generated_id = ID_generator(data= data, used_id= used_id, name= input_NAME, contact_number= input_CONTACT_NUMBER, email_address= input_EMAIL_ADDRESS, event_id= input_EVENT_ID)
        
    while True:
        input_confirmation_add_data = input(f"Are you sure you want to add data with Member ID {value['MEMBER ID']}? [Y/N]: ").upper().strip()
        print()
        if input_confirmation_add_data == 'Y':
            data = pd.concat([data, pd.DataFrame.from_dict(value, orient= 'index').T], ignore_index= True)
            
            print('\nData Saved')
            data.to_excel(members_path, index=False)

            used_id.loc[len(used_id)] = generated_id
            used_id.to_excel(used_membersID_path, index= False)
            print(tabulate(data, headers='keys', tablefmt='fancy_grid'))
            break
        elif input_confirmation_add_data == 'N':
            break
        else:
            Input_error_message('Invalid input. Input [Y] to proceed or [N] to cancel')

# Menu Update
def Update_data(data, index_change, column_change, value): 
    global member_path  
    while True:
        input_update_data_confirmation = input(f"Are you sure you want to update this value for ID {data.loc[index_change]['MEMBER ID'].values}? [Y/N]: ").upper().strip()
        if input_update_data_confirmation == 'Y':
            data.loc[index_change, column_change] = value      
            data.to_excel(member_path, index=False)
            print(tabulate(data.loc[index_change, :], headers='keys', tablefmt='fancy_grid'))
            break
        
        elif input_update_data_confirmation == 'N':
            print('\nThe update process has been canceled.\n')
            break

        else:
            Input_error_message('Invalid Input. Input [Y] to proceed or [N] to cancel')

def Input_data_to_change(data, event_data):
    while True:
        input_id_update = input('MEMBER ID: ').upper().strip()   

        if input_id_update in data['MEMBER ID'].values:
            print(tabulate(data.loc[data['MEMBER ID'] == input_id_update].values, headers= data.columns, tablefmt='fancy_grid'))
            index_to_update = data.loc[data['MEMBER ID'] == input_id_update].index
            
        else:
            Input_error_message(f'There is no Member with ID: {input_id_update}')
            break
        
        column_to_update = None                   
        while True:                
            input_confirmation_change_data = input('Input [Y] to proceed or [N] to cancel: ').upper().strip()


            if input_confirmation_change_data == 'Y':
                while True:
                    input_column_change = input('Please enter the column name: ').upper().strip()
                    
                    if input_column_change in data.columns:      
                        column_to_update = input_column_change
                        break

                    else:
                        Input_error_message(f'Column {input_column_change} does not exist')
                        continue
                    
                if column_to_update == 'NAME':
                    while True:
                        input_new_NAME = input(f'Input new {input_column_change}: ').title().strip()

                        if Input_member_checker(input_new_NAME, column_to_update, evt= event_data) == True:
                            Update_data(data= data, index_change= index_to_update, column_change= column_to_update, value= input_new_NAME)
                            return
                        else:
                            continue

                elif column_to_update == 'CONTACT NUMBER':
                    while True:
                        input_new_CONTACT_NUMBER = input(f'Input new {input_column_change}: ').title()

                        if Input_member_checker(input_new_CONTACT_NUMBER, column_to_update, evt= event_data) == True:
                            Update_data(data= data, index_change= index_to_update, column_change= column_to_update, value= input_new_NAME.strip())
                            return
                        else:
                            continue

                elif column_to_update == 'EMAIL ADDRESS':
                    while True:
                        input_new_EMAIL_ADDRESS = input(f'Input new {input_column_change}: ').upper().strip()

                        if Input_member_checker(input_new_EMAIL_ADDRESS, column_to_update, evt= event_data) == True:
                            Update_data(data= data, index_change= index_to_update, column_change= column_to_update, value= input_new_EMAIL_ADDRESS)
                            return
                        else:
                            continue

                elif column_to_update == 'EVENT ID':
                    while True:
                        print(tabulate(event_data, headers='keys', tablefmt='fancy_grid'))

                        input_new_EVENT_ID = input(f'Input new {input_column_change}: ').title().strip()

                        if Input_member_checker(input_new_EVENT_ID, column_to_update, evt= event_data) == True:
                            Update_data(data= data, index_change= index_to_update, column_change= column_to_update, value= input_new_EVENT_ID)
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

# Menu Delete
def Delete_data(data, evt):
    global members_path
    input_id_delete = input('MEMBER ID: ').upper().strip()       
    
    if input_id_delete not in data['MEMBER ID'].values:
        Input_error_message(f'{input_id_delete} does not exist')
        return
    
    index_to_delete = data.loc[data['MEMBER ID'] == input_id_delete].index         
    print(tabulate(data.loc[data['MEMBER ID'] == input_id_delete], headers= data.columns, tablefmt='fancy_grid'))

    while True:
        input_confirmation_delete_data = input(f"Are you sure you want to delete data with ID {data.loc[index_to_delete, 'MEMBER ID'].values}? [Y/N]: ").upper().strip()
        if input_confirmation_delete_data == 'Y':
            data = data.drop(index_to_delete)
            data.to_excel(members_path, index=False)
            print('\nData has been successfully deleted\n')
            break

        elif input_confirmation_delete_data == 'N':
            print('\nThe deletion process has been canceled\n')
            break
        
        else:
            Input_error_message('Invalid input. Input [Y] to proceed or [N] to cancel')
            continue

def Read_file(path, sheet_name):
    pd.read_excel(path, sheet_name, dtype= 'object')

def Save_file(path, sheet_name):
    pd.to_excel(path, sheet_name, index= False)

def Main_flow():
    while True:
        global members_path, events_path, used_membersID_path, used_eventsID_path
        # Define DF
        members_path = r"./Members_Data.xlsx"
        events_path = r"./Events_Data.xlsx"
        used_membersID_path = r'./Used_MembersID.xlsx'
        used_eventsID_path = r'./Used_EventsID.xlsx'
        

        members_data = pd.read_excel(members_path, dtype= 'str')
        event_data = pd.read_excel(events_path, dtype= 'str')
        used_members_ID = pd.read_excel(used_membersID_path, dtype= 'object')
        used_events_ID = pd.read_excel(used_membersID_path, dtype= 'object')

        main_menu_input = Call_menu(['Members Data', 'Add Data', 'Change Data', 'Delete Data', 'Exit'], menu_title= 'Main Menu')
        if main_menu_input == '1':      # Menu Read
            while True:
                sub_menu_1_input = Call_menu(['Show All Data', 'Search ID', 'Main Menu'], menu_title= 'Employee Data')
                if sub_menu_1_input == '1':     # Show all members data
                    print(tabulate(members_data, headers='keys', tablefmt='fancy_grid'))
                elif sub_menu_1_input == '2':   # Show specific data based on ID
                    Show_specific_data(members_data)
                elif sub_menu_1_input == '3':   # Return to main menu
                    break
                else:
                    Menu_error_message(sub_menu_1_input)

        elif main_menu_input == '2':    # Menu Create
            while True:
                sub_menu_2_input = Call_menu(['Add Member Data', 'Main Menu'], menu_title= 'Add Data')
                if sub_menu_2_input == '1':     # Add new member
                    Input_data_member(data= members_data, used_id= used_members_ID, evt= event_data , value= temporary_members_value)
                elif sub_menu_2_input == '2':   # Return to main menu
                    break
                else:
                    Menu_error_message(sub_menu_2_input)

        elif main_menu_input == '3':    # Menu Update
            while True:
                sub_menu_3_input = Call_menu(['Change Member Data', 'Main Menu'], menu_title= 'Change Data')
                if sub_menu_3_input == '1':     # Change member data based on ID
                    Input_data_to_change(data= members_data, evt= event_data)
                elif sub_menu_3_input == '2':   # Return to main menu
                    break
                else:
                    Menu_error_message(sub_menu_3_input)

        elif main_menu_input == '4':    # Menu Delete
            while True:
                sub_menu_4_input = Call_menu(['Delete Member Data', 'Main Menu'], menu_title= 'Delete Data')
                if sub_menu_4_input == '1':     # Delete employee data based on ID
                    Delete_data(data= members_data, evt=event_data)
                elif sub_menu_4_input == '2':   # Return to main menu
                    break
                else:
                    Menu_error_message(sub_menu_4_input)

        elif main_menu_input == '5':    
            exit()
        else:
            Menu_error_message(main_menu_input)



def null_test():
    
    global members_path, events_path, used_membersID_path, used_eventsID_path
    # Define DF
    members_path = r"./Members_Data.xlsx"
    events_path = r"./Events_Data.xlsx"
    used_membersID_path = r'./Used_MembersID.xlsx'
    used_eventsID_path = r'./Used_EventsID.xlsx'
    
    
    members_data = pd.read_excel(members_path, dtype= 'str')
    event_data = pd.read_excel(events_path, dtype= 'str')
    used_members_ID = pd.read_excel(used_membersID_path, dtype= 'object')
    used_events_ID = pd.read_excel(used_membersID_path, dtype= 'object')

    missing_data = members_data.isnull()
    print(missing_data)

        
# Main_flow()
