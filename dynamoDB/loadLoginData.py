import sys
from pathlib import Path

project_root = Path(__file__).parent.parent

from utils.utils import load
from utils.DynamoDB import DynamoDB

loginJson = project_root / "artifacts" / "logins.json"

def loadData():
    
    # Get list of logins -------------------------------------------------------------------------------

    data = load(loginJson)
    songs = data["logins"]

    # Initialize DynamoDB -------------------------------------------------------------------------------

    dndb = DynamoDB()

    dndb.get_table("login")

    if dndb.workingTable is None:
        print("Could not load table, aborting.")
        sys.exit(-1)


    # ----------------------------------------------------------------------------------------------------
    # Loading data
    # -----------------------------------------------------------------------------------------------------

    for i, song in enumerate(songs):

        if (i + 1) % 25 == 0:
            print(f"Loading credentials {i+1} / {len(songs)}")

        if (i == len(songs) - 1):
            print(f"Loading credentials {i+1} / {len(songs)}")

        dndb.put_item(song)

        print(f"Done! loaded {len(songs)} credentials")

if __name__ == "__main__":
    loadData()
