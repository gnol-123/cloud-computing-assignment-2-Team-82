import boto3
from typing import Any
from boto3.dynamodb.conditions import Key,  Attr

"""
Wrapping boto3 dynamodb in DynamoDB class
Senglong Te
"""

class DynamoDB:

    def __init__(self):

        self.dynamodb = boto3.resource('dynamodb')
        self.workingTable = None

    # ---------------------------------------------------------------------------------------------------------------------------------

    def create_new_table(self, tableName:str, KeySchema: Any, AttributeDefinitions: Any, ProvisionedThroughput: Any, GlobalSecondaryIndexes=None, LocalSecondaryIndexes=None):

        """
        Make a dynamoDB table.

        @params tableName: Name for new table.
        @params KeySchema: Key Schema for name and attribute types, list of dicts \n\te.g. [{'AttributeName':'title','KeyType':'HASH'}   ,  {...}]
        @params AttributeDefinitions: List of Dicts defining key types \n\t e.g. [{'AttributeName': 'title', 'AttributeType': 'S', {...}]
        @params ProvisionedThroughput: Dict defining Input/Output ProvisioningThroughput (IOPT) \n\t e.g. {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        @params GlobalSecondaryIndexes: (optional**) List of Dict defining Global Secondary Index \n\t e.g. [{'IndexName': 'year-index', 'KeySchema': [...], 'Projection': {...}, 'ProvisionedThroughput': {...}}]
        @params LocalSecondaryIndexes
        """

        # make dynamoDB table
        try:

            params = {
                'TableName': tableName,
                'KeySchema': KeySchema,
                'AttributeDefinitions': AttributeDefinitions,
                'ProvisionedThroughput': ProvisionedThroughput
            }

            if GlobalSecondaryIndexes is not None:
                params['GlobalSecondaryIndexes'] = GlobalSecondaryIndexes

            if LocalSecondaryIndexes is not None:
                params['LocalSecondaryIndexes'] = LocalSecondaryIndexes

            table = self.dynamodb.create_table(**params)
            table.wait_until_exists()
            print(table.item_count)
            
        except Exception as e:
            print(f"Failed to create table: {e}")
            

    # ---------------------------------------------------------------------------------------------------------------------------------

    def get_table(self, tableName:str):

        """
        Get table from name and set as current table

        @params tableName: name of table to fetch
        """

        try:
            print(f"fetching table...")

            self.workingTable = self.dynamodb.Table(tableName)  

            print(f"Successfully fetched table: {tableName}\n Table created at: {self.workingTable.creation_date_time}")

        except Exception as e:
            print(f"Failed to fetch table: {e}")
            self.workingTable = None

    # ---------------------------------------------------------------------------------------------------------------------------------

    def has_table(self):
        """
        Check for active table
        """
        if not self.workingTable:
            raise RuntimeError("No table do get_table()")

    # ---------------------------------------------------------------------------------------------------------------------------------

    def put_item(self, item: dict):

        """
        Add item to table.

        @params item: item in dict form
        """

        self.has_table()

        try:
            self.workingTable.put_item(
                Item=item
            )
        except Exception as e:
            print(f"Failed to delete item: {e}")

    # ---------------------------------------------------------------------------------------------------------------------------------

    def get_item(self, key:dict):

        """
        Get item from table

        @params key: key in dict form \ne.g. Key={ 'username': 'janedoe' , 'last_name': 'Doe' }
        """

        self.has_table()

        try:
            response = self.workingTable.get_item(
                Key=key
            )

            return response.get('Item')
        
        except Exception as e:
            print(f"Failed to delete item: {e}")

    # ---------------------------------------------------------------------------------------------------------------------------------
  
    def delete_item(self, key:dict):
        """
        Delete item given key s
        @params: key in dict form \ne.g. Key={ 'username': 'janedoe' , 'last_name': 'Doe' }
        """

        self.has_table()

        try:
            self.workingTable.delete_item(
                Key=key
            )
        except Exception as e:
            print(f"Failed to delete item: {e}")

    # ---------------------------------------------------------------------------------------------------------------------------------

    def update_item(self, key:dict, attributeToUpdate: str, newVal: Any):

        """
        Update item given key in dict form, attribute to update, new value.

        @params key: Dict with partition and sort key \n\t e.g. {'title': '1904', 'artist': 'The Tallest Man on Earth'}
        @params attributeToUpdate: Name of attribute to update \n\t e.g. 'year'
        @params newVal: New value to update \n\t e.g. '2021'
        """

        self.has_table()

        try:
            self.workingTable.update_item(
                Key=key,
                UpdateExpression=f'SET {attributeToUpdate} = :val1',
                ExpressionAttributeValues={
                    ':val1': newVal
                }
            )
        except Exception as e:
            print(f"Failed to update attribute: {e}")

    # ---------------------------------------------------------------------------------------------------------------------------------

    def query(self, keyString:str,query: str,  indexName: str = None, sortKeyString: str = None, sortKeyQuery: str = None):

        """
        Query for string given query and key to query

        @params keyString: key of attr to query \n\t e.g. 'title'
        @params query: query to parse \n\t e.g. '1904'
        @params indexName: (optional**) name of index to query
        @params sortKeyString: (optional**) sort key attribute name \n\t e.g. 'album'
        @params sortKeyQueury: (optional**) sort key attribute value to query e.g. 'randomAlbum'
        """

        try:
            keyCondition = Key(keyString).eq(query)

            if sortKeyString and sortKeyQuery:
                keyCondition = keyCondition & Key(sortKeyString).eq(sortKeyQuery)

            params = {
                'KeyConditionExpression': keyCondition
            }

            if indexName:
                params['IndexName'] = indexName

            response = self.workingTable.query(**params)
            return response.get('Items')

        except Exception as e:
            print(f"Failed to query: {e}")



    def delete_table(self, tableName:str):

        """
        Delete table given tableName

        @params tableName: tableName as string
        """

        self.get_table(tableName=tableName)
        self.workingTable.delete()