import math

def convert_nan_to_string(p_input):
    if type(p_input) is not str:
        if math.isnan(p_input):
            return ""
    return p_input


def validate_before_saving(mcfName, yearOfBirth, state):
    returnDict = {}
    if type(mcfName) is not str:
        if math.isnan(mcfName):
            return {} # coz mcfName is compulsary
    else:
        returnDict["mcfName"] = mcfName
        
    if type(yearOfBirth) is not str:
        if math.isnan(yearOfBirth):
            # returnDict["yearOfBirth"] = ""
            return {} # coz yearOfBirth is compulsary
    else:
        returnDict["yearOfBirth"] = yearOfBirth
        
    if type(state) is not str:
        if math.isnan(state):
            # returnDict["yearOfBirth"] = ""
            return {} # coz state is compulsary
    else:
        returnDict["state"] = state
        
        
    return returnDict
