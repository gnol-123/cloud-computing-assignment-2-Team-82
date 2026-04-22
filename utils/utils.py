import json

def load(inpJson):

    # load Json file
    try:
        with open(inpJson) as j:
            data = json.load(j)
            return data
        
    except FileNotFoundError:
        print("Couldnt find file")
        return -1
    except json.JSONDecodeError:
        print("Error decoding raw data json file")
        return -1