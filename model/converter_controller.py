# controller/converter_controller.py

from scanfile_handler import find_exr_files
import os

def load_scan_data(folder_path):
    """EXR 파일을 기반으로 테이블에 보여줄 데이터를 구성"""
    file_list = find_exr_files(folder_path)
    rows = []

    for f in file_list:
        file_name = os.path.basename(f)
        shot_name = ""  # 사용자가 직접 입력할 수 있도록 비워둠
        version = "v001"  # 기본 버전
        rows.append({
            "thumbnail": f,       # 썸네일 경로 (나중에 이미지 처리)
            "file_name": file_name,
            "shot_name": shot_name,
            "version": version,
            "path": f
        })

    return rows
