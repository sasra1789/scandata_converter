# model/scanfile_handler.py

import os

def find_exr_files(folder_path):
    """주어진 폴더에서 .exr 파일만 찾아 리스트로 반환"""
    exr_files = []
    # 인식 못해서 디렉토리 안 디렉토리 까지 찾도록 바뚬 
    for root, _, files in os.walk(folder_path):
        for f in files:
            if f.lower().endswith(".exr"):
                exr_files.append(os.path.join(root, f))

    return exr_files
