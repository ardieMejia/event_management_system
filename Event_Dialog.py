import unittest
import pandas as pd
from tabulate import tabulate
import random
from Models.member import Member 
from Models.event import Event
from crud import Crud





# member = Member(r"./Members_Data.xlsx", r'./Used_MembersID.xlsx', "MEMBER ID")
event = Event(r"./Events_Data.xlsx", r'./Used_EventsID.xlsx', "EVENT ID") 
crud = Crud() 




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

    



        


                

            
            
            
def Main_flow():

    #     # Define DF

    
    print("done")


    while True:
        main_menu_input = Call_menu(['Events Data', 'Add Data', 'Change Data', 'Delete Data', 'Exit'], menu_title= 'Main Menu')
        if main_menu_input == '1':      # Menu Read
            while True:
                sub_menu_1_input = Call_menu(['Show All Data', 'Search ID', 'Main Menu'], menu_title= 'Employee Data')
                if sub_menu_1_input == '1':     # Show all members data
                    print("show")
                    event.data = event.data.astype(str)
                    print(tabulate(event.data, headers='keys', tablefmt='fancy_grid', floatfmt='14.0f'))
                elif sub_menu_1_input == '2':   # Show specific data based on ID
                    crud.Show_specific_data(event)
                elif sub_menu_1_input == '3':   # Return to main menu
                    break
                else:
                    Menu_error_message(sub_menu_1_input)

                
        elif main_menu_input == '2':    # Menu Create
            while True:
                sub_menu_2_input = Call_menu(['Add Member Data', 'Main Menu'], menu_title= 'Add Data')
                if sub_menu_2_input == '1':     # Add new member
                    crud.Input_data_member(member,event)
                elif sub_menu_2_input == '2':   # Return to main menu
                    break
                else:
                    Menu_error_message(sub_menu_2_input)
                    
        elif main_menu_input == '3':    # Menu Update
            while True:
                sub_menu_3_input = Call_menu(['Change Member Data', 'Main Menu'], menu_title= 'Change Data')
                if sub_menu_3_input == '1':     # Change member data based on ID
                    crud.Input_data_to_change(member,event)
                elif sub_menu_3_input == '2':   # Return to main menu
                    break
                else:
                    Menu_error_message(sub_menu_3_input)
                    

        elif main_menu_input == '4':    # Menu Delete
            while True:
                sub_menu_4_input = Call_menu(['Delete Member Data', 'Main Menu'], menu_title= 'Delete Data')
                if sub_menu_4_input == '1':     # Delete employee data based on ID
                    crud.Delete_data(member)
                elif sub_menu_4_input == '2':   # Return to main menu
                    break
                else:
                    Menu_error_message(sub_menu_4_input)
                    
        elif main_menu_input == '5':    
            exit()
        else:
            Menu_error_message(main_menu_input)
            


        
Main_flow()
