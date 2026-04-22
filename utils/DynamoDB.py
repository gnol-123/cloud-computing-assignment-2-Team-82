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

    def create_new_table(self, tableName:str, KeySchema: Any, AttributeDefinitions: Any, ProvisionedThroughput: Any):

        """
        Make a dynamoDB table.

        @params tableName: Name for new table.
        @params KeySchema: Key Schema for name and attribute types, list of dicts \ne.g. [ {   'AttributeName':'username'    ,   'KeyType':'HASH'     }   ,  {...}    ]
        @para
        """

        # make dynamoDB table
        try:
            table = self.dynamodb.create_table(TableName=tableName, 
                                            KeySchema=KeySchema, 
                                            AttributeDefinitions=AttributeDefinitions, 
                                            ProvisionedThroughput=ProvisionedThroughput)
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

        @params  
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

    def query(self, keyString:str,query: str):

        """
        Query for string given query and key to query

        @param keyString: key of attr to query
        @param query: query to parse
        """

        response = self.workingTable.query(
            KeyConditionExpression=Key(keyString).eq(query)
        )

        return response

    def delete_table(self, tableName:str):

        """
        Delete table given tableName

        @params tableName: tableName as string
        """

        self.get_table(tableName=tableName)
        self.workingTable.delete()