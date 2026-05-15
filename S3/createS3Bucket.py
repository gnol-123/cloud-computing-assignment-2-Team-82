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
    bucket_name = "cloud-computing-a2-s4054917-test" 

    client.create_bucket(bucketName=bucket_name)
    client.get_bucket(bucketName=bucket_name)
    try:
        client.s3.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls':       True,
                'IgnorePublicAcls':      True,
                'BlockPublicPolicy':     True,
                'RestrictPublicBuckets': True
            }
        )
        print('Public access block enabled')
    except Exception as e:
        print(f'  Warning: Could not enable block public access: {e}')



if __name__ == "__main__":
    main()