import sys
from pathlib import Path

project_root = Path(__file__).parent.parent

from utils.utils import load
from utils.DynamoDB import DynamoDB

songsJson = project_root / "artifacts" / "2026a2_songs.json"

def loadData():
    
    # Get list of songs  -------------------------------------------------------------------------------

    data = load(songsJson)
    songs = data["songs"]

    # Initialize DynamoDB -------------------------------------------------------------------------------

    dndb = DynamoDB()

    dndb.get_table("music")

    if dndb.workingTable is None:
        print("Could not load table, aborting.")
        sys.exit(-1)


    # ----------------------------------------------------------------------------------------------------
    # Loading data
    # -----------------------------------------------------------------------------------------------------

    for i, song in enumerate(songs):

        if (i + 1) % 25 == 0:
            print(f"Loading song {i+1} / {len(songs)}")

        if (i == len(songs) - 1):
            print(f"Loading song {i+1} / {len(songs)}")

        dndb.put_item(song)

    print(f"Done! loaded {len(songs)} songs")

if __name__ == "__main__":
    loadData()
