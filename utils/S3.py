import boto3
from typing import Any

"""
Wrapping S3 in S3 class
Senglong Te
"""

class S3:

    # ---------------------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        try:
            self.s3 = boto3.client('s3')
        except Exception as e:
            print(f"failed to intialise S3: {e}")
        
        self.workingBucket = None

    # ---------------------------------------------------------------------------------------------------------------------------------

    def create_bucket(self, bucketName:str, region:str ="us-east-1"):
        """
        Create an S3 Bucket

        @params bucketName: name of bucket
        @params region: bucket region (default = "us-east-1")
        """
        try:
            if region == "us-east-1":

                self.s3.create_bucket(
                    Bucket=bucketName
                )
            else:
                self.s3.create_bucket(
                    Bucket=bucketName,
                    CreateBucketConfiguration={"LocationConstraint": region}
                )

            print(f"Successfully created bucket")
        except Exception as e:
            print(f"Failed to create bucket: {e}")

    # ---------------------------------------------------------------------------------------------------------------------------------

    def get_bucket(self, bucketName:str):
        """
        set current working bucket to given bucket name

        @params bucketName: name of bucket to retrieve
        """

        try:
            self.s3.head_bucket(Bucket=bucketName)
            self.workingBucket = bucketName
            print(f"Retrieved working bucket: {bucketName}")

        except Exception as e:
            print(f"Failed to get working bucket: {e}")
            self.workingBucket = None

    # ---------------------------------------------------------------------------------------------------------------------------------
        
    def has_bucket(self):
        """
        Check for current working bucket
        """
        if not self.workingBucket:
            raise RuntimeError("No bucket loaded. Call get_bucket() first.")
        else:
            print(f"Current working bucket: {self.workingBucket}")

    # ---------------------------------------------------------------------------------------------------------------------------------

    def upload(self, filePath:str, key:str):

        """
        Upload file to bucket as a Key

        @params filePath: Path to local file to upload
        @params key: name or path of file in S3 e.g. 'img/1904.jpg'
        """

        self.has_bucket()

        try:

            self.s3.upload_file(filePath,self.workingBucket, key)
            print(f"Successfully uploaded {key}!")

        except Exception as e:
            print(f"Failed to upload: {e}")

    # ---------------------------------------------------------------------------------------------------------------------------------

    def download(self, key:str, filePath:str): 
        """
        Download specific key from working bucket to filePath

        @params key: name of object to download from S3
        @params filePath: path to dump downloaded object
        """

        try:
            self.s3.download_file(self.workingBucket, key, filePath)
            print(f"Successfully downloaded {key}")

        except Exception as e:
            print(f"Failed to download: {e}")

    # ---------------------------------------------------------------------------------------------------------------------------------

    def delete(self, key:str):
        """
        Delete object from working bucket given key

        @params key: name of object to delete e.g. 'img/1904.jgp'
        """

        self.has_bucket()

        try:
            self.s3.delete_object(Bucket=self.workingBucket, Key=key)
            print(f"Successfully deleted {key}")

        except Exception as e:
            print(f"Failed to delete file: {e}")

    # ---------------------------------------------------------------------------------------------------------------------------------

    def list_bucket(self, dir:str=""):
        """
        list items in bucket directory or prefix

        @params dir: Key prefix to print e.g. 'img/'
        """

        try:
            response = self.s3.list_objects_v2(Bucket=self.workingBucket, Prefix=dir)
            items = response.get('Contents', [])
            return [item['Key'] for item in items]

        except Exception as e:
            print(f"Failed to list files: {e}")

    # ---------------------------------------------------------------------------------------------------------------------------------

    def delete_bucket(self, bucketName: str):
        """
        Delete bucket given name.

        @params bucketName: name of bucket to delete
        """
        try:
            self.get_bucket(bucketName)
            self.s3.delete_bucket(Bucket=bucketName)
            self.workingBucket = None
            print(f"Successfully deleted bucket: {bucketName}")

        except Exception as e:
            print(f"Failed to delete bucket: {e}")

    # ---------------------------------------------------------------------------------------------------------------------------------

