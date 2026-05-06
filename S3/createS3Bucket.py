import sys
from pathlib import Path
import json
import requests

project_root = Path(__file__).parent.parent

from utils.utils import load
from utils.S3 import S3

songsJson = project_root / "artifacts" / "2026a2_songs.json"


def main():

    # S3 Bucket initialization ----------------------------------------------------------------------------------

    print(f"Initialising S3")
    client = S3()

    print(f"Creating bucket...")

    # *** MUST BE UNIQUE USE YOUR OWN STUDENT NUMBER (TODO) *** #
    bucket_name = "cloud-computing-a2-s4054917" 

    client.create_bucket(bucketName=bucket_name)
    client.get_bucket(bucketName=bucket_name)
    try:
        client.s3.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls':       False,
                'IgnorePublicAcls':      False,
                'BlockPublicPolicy':     False,
                'RestrictPublicBuckets': False
            }
        )
        print('Public access block disabled')
    except Exception as e:
        print(f'  Warning: Could not disable block public access: {e}')

    try:
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid":       "PublicReadGetObject",
                    "Effect":    "Allow",
                    "Principal": "*",
                    "Action":    "s3:GetObject",
                    "Resource":  f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }
        client.s3.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(policy)
        )
        print('Bucket policy set - public read enabled')
    except Exception as e:
        print(f'Warning: Could not set bucket policy: {e}')




if __name__ == "__main__":
    main()