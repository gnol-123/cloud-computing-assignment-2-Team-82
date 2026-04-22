from pathlib import Path

project_root = Path(__file__).parent.parent

from utils.DynamoDB import DynamoDB

def createTable():

    # Initialise DynamoDB class --------------------------------------------------------------------------

    print("Initialising Client")

    dndb = DynamoDB()

    print("Making table")

    # ---------------------------------------------------------------------------------
    # THIS IS SAMPLE SCHEMA FOR NOW WE STILL HAVE TO DECIDE HOW WE WANT TO DESIGN IT.
    # ---------------------------------------------------------------------------------

    tableName = "song2026_A2"

    # DEFINE PARTITION KEY AND SORT KEY
    keySchema = [
        {
            'AttributeName': 'title',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'artist',
            'KeyType': 'RANGE'
        }
    ]

    # DEFINE ATTRIBUTE TYPE

    AttributeDefinitions=[
        {
            'AttributeName': 'title',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'artist',
            'AttributeType': 'S'
        }
    ]

    # IOPT
    ProvisionedThroughput= {
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }

    # SECONDARY INDEX 
    
    GSI=[
        {
            'IndexName': 'year-index',
            'KeySchema': [
                {'AttributeName': 'year', 'KeyType': 'HASH'}
            ],
            'Projection': {'ProjectionType': 'ALL'},
            'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        }
    ]


    # Create table ---------------------------------------------------------------------------------------------------------------------------------------------------
    
    dndb.create_new_table(tableName=tableName, KeySchema=keySchema, AttributeDefinitions=AttributeDefinitions, ProvisionedThroughput=ProvisionedThroughput, GlobalSecondaryIndexes=GSI)

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    createTable()