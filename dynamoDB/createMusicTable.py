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

    tableName = "music"

    # DEFINE PARTITION KEY AND SORT KEY ------------------------------------------------------------------------------------------------------

    keySchema = [
        {
            'AttributeName': 'artist',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'title',
            'KeyType': 'RANGE'
        }
    ]

    # DEFINE ATTRIBUTE TYPE ------------------------------------------------------------------------------------------------------------------

    AttributeDefinitions=[
        {'AttributeName': 'title', 'AttributeType': 'S'},
        {'AttributeName': 'artist', 'AttributeType': 'S'},
        {'AttributeName': 'year', 'AttributeType': 'S'},
        {'AttributeName': 'album', 'AttributeType': 'S'}
    ]

    # IOPT ------------------------------------------------------------------------------------------------------------------------------------

    ProvisionedThroughput= {
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }

    # SECONDARY INDEXEX -----------------------------------------------------------------------------------------------------------------------

    GSI=[
        {
            'IndexName': 'year-gsi',
            'KeySchema': [
                {'AttributeName': 'year', 'KeyType': 'HASH'}
            ],
            'Projection': {'ProjectionType': 'ALL'},
            'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        },
        {
            'IndexName': 'album-gsi',
            'KeySchema': [
                {'AttributeName': 'album', 'KeyType': 'HASH'}
            ],
            'Projection': {'ProjectionType': 'ALL'},
            'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        },
        {
            'IndexName': 'title-gsi',
            'KeySchema': [
                {'AttributeName': 'title', 'KeyType': 'HASH'},
                {'AttributeName': 'artist', 'KeyType': 'RANGE'}
            ],
            'Projection': {'ProjectionType': 'ALL'},
            'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        }
    ]

    LSI=[
        {
            'IndexName': 'album-lsi',
            'KeySchema': [
                {'AttributeName': 'artist', 'KeyType': 'HASH'},  
                {'AttributeName': 'album', 'KeyType': 'RANGE'} 
            ],
            'Projection': {'ProjectionType': 'ALL'}
        },
        {
            'IndexName': 'year-lsi',
            'KeySchema': [
                {'AttributeName': 'artist', 'KeyType': 'HASH'},  
                {'AttributeName': 'year', 'KeyType': 'RANGE'} 
            ],
            'Projection': {'ProjectionType': 'ALL'}
        }
    ]


    # Create table ---------------------------------------------------------------------------------------------------------------------------------------------------
    
    dndb.create_new_table(tableName=tableName, KeySchema=keySchema, AttributeDefinitions=AttributeDefinitions, ProvisionedThroughput=ProvisionedThroughput, GlobalSecondaryIndexes=GSI, LocalSecondaryIndexes=LSI)
    print(f"successfully made table!...")

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    createTable()