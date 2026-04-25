from pathlib import Path

project_root = Path(__file__).parent.parent

from utils.DynamoDB import DynamoDB

def createTable():

    # Initialise DynamoDB class --------------------------------------------------------------------------

    print("Initialising Client")

    dndb = DynamoDB()

    print("Making table...")

    # ---------------------------------------------------------------------------------
    # Table attributes
    # ---------------------------------------------------------------------------------

    tableName = "login"

    # DEFINE PARTITION KEY AND SORT KEY ------------------------------------------------------------------------------------------------------

    keySchema = [
        {
            'AttributeName': 'email',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'user_name',
            'KeyType': 'RANGE'
        }
    ]

    # DEFINE ATTRIBUTE TYPE ------------------------------------------------------------------------------------------------------------------

    AttributeDefinitions=[
        {'AttributeName': 'email', 'AttributeType': 'S'},
        {'AttributeName': 'user_name', 'AttributeType': 'S'},
    ]

    # IOPT ------------------------------------------------------------------------------------------------------------------------------------

    ProvisionedThroughput= {
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }


    # Create table ---------------------------------------------------------------------------------------------------------------------------------------------------
    
    dndb.create_new_table(tableName=tableName, KeySchema=keySchema, AttributeDefinitions=AttributeDefinitions, ProvisionedThroughput=ProvisionedThroughput)
    print(f"successfully made table!...")

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    createTable()