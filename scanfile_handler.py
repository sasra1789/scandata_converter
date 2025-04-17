# model/scanfile_handler.py

import os

def find_exr_files(folder_path):
    """주어진 폴더에서 .exr 파일만 찾아 리스트로 반환"""
    return [
        os.path.join(folder_path, f)
        for f in sorted(os.listdir(folder_path))
        if f.lower().endswith(".exr")
    ]
