import pandas as pd

from private.consts.file_paths import BASE_PATH

def get_mappings(path: str = BASE_PATH) -> pd.DataFrame:
    return pd.read_csv(f"{path}/security_mapping.csv")