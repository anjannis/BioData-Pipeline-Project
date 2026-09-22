import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"

print(RAW_DIR)


def load_info() -> pd.DataFrame:
    """
    Load the STRING protein info file into a DataFrame.
    """
    path = RAW_DIR / "9606.protein.info.v12.0.txt"

    df = pd.read_csv(path, sep="\t", header=0)
    return df

def load_links() -> pd.DataFrame:
    """
    Load the STRING protein link file into a Dataframe.
    """
    path = RAW_DIR / "9606.protein.links.v12.0"

    df = pd.read_csv(path, sep="\t", header=0)
    return df

if __name__ == "__main__":
    df = load_info()
    print(df.head())
    print(df.shape)
    print(df.dtypes)