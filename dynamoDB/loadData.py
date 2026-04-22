from pathlib import Path

project_root = Path(__file__).parent.parent

from utils.utils import load
from utils.DynamoDB import DynamoDB

songsJson = project_root / "artifacts" / "2026a2_songs.json"

def loadData():
    
    # Get list of songs  -------------------------------------------------------------------------------

    data = load(songsJson)
    songs = data["songs"]

    # ----------------------------------------------------------------------------------------------------
    # Loading data (TODO)
    # -----------------------------------------------------------------------------------------------------

    for i, songs in enumerate(songs):

        if (i + 1) % 25 == 0:
            print(f"Loading song {i+1} / {len(songs)}")
        
        pass






if __name__ == "__main__":
    loadData()
