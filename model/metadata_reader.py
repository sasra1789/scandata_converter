# 📁 model/metadata_reader.py
import os
import csv
import subprocess
from model.converter import convert_exr_to_jpg_single_frame_ffmpeg

def extract_metadata_from_exr(filepath):
    """
    exiftool을 사용해 EXR 파일의 메타데이터를 딕셔너리로 추출
    """
    metadata = {}
    try:
        result = subprocess.run([
            "exiftool", filepath
        ], capture_output=True, text=True, check=True)

        for line in result.stdout.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()
    except Exception as e:
        print(f"[Error] 메타데이터 추출 실패: {filepath}", e)

    return metadata

def save_metadata_csv(metadata_list, csv_path):
    """
    딕셔너리 리스트를 CSV로 저장
    """
    if not metadata_list:
        print("[Warning] 저장할 메타데이터 없음")
        return

    keys = list(metadata_list[0].keys())
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(metadata_list)

    print(f"[CSV] metadata 저장 완료: {csv_path}")


# model/metadata_reader.py
import csv

def load_metadata_csv(csv_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def generate_metadata_from_folder(scan_dir, csv_path):
    """
    EXR 파일 목록에서 썸네일 생성 및 메타데이터 수집 후 CSV 저장
    """
    from scanfile_handler import find_exr_files, auto_generate_shot_name

    exr_files = find_exr_files(scan_dir)
    if not exr_files:
        print("[Info] EXR 없음 - 메타 생성 생략")
        return

    os.makedirs("/home/rapa/westworld_serin/scan_thumbs", exist_ok=True)
    metadata_list = []
    for exr_path in exr_files:
        shot_name = auto_generate_shot_name(exr_path)
        thumb_path = f"/home/rapa/westworld_serin/scan_thumbs/{shot_name}.jpg"
        convert_exr_to_jpg_single_frame_ffmpeg(exr_path, thumb_path)

        meta = extract_metadata_from_exr(exr_path)
        meta.update({
            "thumbnail": thumb_path,
            "path": exr_path,
            "check": True,
            "shot_name": shot_name,
            "version": "v001",
            "seq_name": "",
            "roll": "",
            "scan_name": "",
            "clip_name": "",
            "type": "org"
        })
        metadata_list.append(meta)

    save_metadata_csv(metadata_list, csv_path)


def generate_metadata_csv(scan_dir, csv_path):
    """
    주어진 디렉토리(scan_dir) 내의 .exr 파일들의 메타데이터를 추출하여
    metadata.csv로 저장하는 함수
    """
    # EXR 파일 목록 추출
    exr_files = [f for f in os.listdir(scan_dir) if f.endswith(".exr")]
    if not exr_files:
        print("❌ EXR 파일이 없습니다.")
        return

    # 전체 경로로 변환
    exr_paths = [os.path.join(scan_dir, f) for f in exr_files]

    # ffmpeg나 exiftool이 경로에 없다면 에러 가능
    try:
        cmd = ["exiftool", "-csv"] + exr_paths
        with open(csv_path, "w", encoding="utf-8") as f:
            subprocess.run(cmd, stdout=f)
        print(f"✅ metadata.csv 저장 완료: {csv_path}")
    except Exception as e:
        print(f"❌ metadata.csv 생성 실패: {e}")