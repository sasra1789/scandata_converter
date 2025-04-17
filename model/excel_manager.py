# 📁 model/excel_manager.py

import pandas as pd
import os

def save_to_excel(data: list[dict], save_path: str):
    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    df.to_excel(save_path, index=False)


def load_shotnames_from_excel(excel_path: str) -> dict:
    if not os.path.exists(excel_path):
        return {}
    df = pd.read_excel(excel_path)
    result = {}
    for _, row in df.iterrows():
        if 'scan_path' in row and 'shot_name' in row:
            result[row['scan_path']] = row['shot_name']
    return result