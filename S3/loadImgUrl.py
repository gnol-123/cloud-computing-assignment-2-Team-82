import sys
from pathlib import Path
import requests

project_root = Path(__file__).parent.parent

from utils.utils import load
from utils.S3 import S3

songsJson = project_root / "artifacts" / "2026a2_songs.json"


def main():

    # Loading Data ----------------------------------------------------------------------------------------------

    print(f"Loading Data...")

    data = load(songsJson)
    songs = data["songs"]

    # S3 Bucket initialization ----------------------------------------------------------------------------------

    print(f"Getting S3 Bucket...")
    client = S3()

    # *** CHANGE TO THE BUCKET NAME YOU CREATED (TODO) *** #
    client.get_bucket("cloud-computing-a2-s4054917") 

    for i, song in enumerate(songs):

        if (i + 1) % 5 == 0:
            print("-"*56)
            print(f"uploading images {i+1} / {len(songs)}")
            print("-"*56)

        if (i == len(songs) - 1):
            print("-"*56)
            print(f"uploading images {i+1} / {len(songs)}")
            print("-"*56)

        # get image bytes
        img = requests.get(song['img_url']).content
        # store as img/{artist}
        key = f"img/{song['artist']}"

        #upload
        client.upload_bytes(data=img, key=key)


    print(f"Done uploaded {len(songs)} images!")

if __name__ == "__main__":
    main()