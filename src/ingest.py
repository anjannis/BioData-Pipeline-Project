import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"

def load_info(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    """
    Load the STRING protein info file into a DataFrame.
    """
    path = raw_dir / "9606.protein.info.v12.0.txt"

    df = pd.read_csv(path, sep="\t")
    df = df.rename(columns={"#string_protein_id": "string_protein_id"})
    return df

def load_links(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    """
    Load the STRING protein link file into a Dataframe.
    """
    path = raw_dir / "9606.protein.links.v12.0.txt"

    df = pd.read_csv(path, sep=" ", dtype={"combined_score": "int16"})
    return df

if __name__ == "__main__":
    df_info = load_info()
    print(df_info.head())
    print(df_info.shape)
    print(df_info.dtypes)

    df_links = load_links()
    print(df_links.head())
    print(df_links.shape)
    print(df_links.dtypes)