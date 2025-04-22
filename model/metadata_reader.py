# exr에서 해상도수, 프레임수, 렌즈 정보 등을 exiftool로 추출하여 저장 
#  model/metadata_reader.py
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


def load_metadata_csv(csv_path):
    """
    metadata.csv를 읽고 썸네일 경로를 절대경로로 변환해서 리턴
    """
    base_dir = os.path.dirname(csv_path)

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        for row in rows:
            # 썸네일 경로가 있으면 절대경로로 변환
            if "thumbnail" in row and row["thumbnail"]:
                row["thumbnail"] = os.path.join(base_dir, row["thumbnail"])

        return rows


#이건가 
def generate_metadata_csv(scan_dir, csv_path):
    """
    EXR 파일들의 메타데이터를 csv로 저장하고,
    각 행에 썸네일 경로 컬럼을 수동으로 삽입 
    """
    exr_files = [f for f in os.listdir(scan_dir) if f.endswith(".exr")]
    if not exr_files:
        print("EXR 파일이 없습니다.")
        return

    exr_paths = [os.path.join(scan_dir, f) for f in exr_files]
    tmp_csv = os.path.join(scan_dir, "tmp_metadata.csv")

    try:
        # 1. exiftool로 tmp csv 생성
        cmd = ["exiftool", "-csv"] + exr_paths
        with open(tmp_csv, "w", encoding="utf-8") as f:
            subprocess.run(cmd, stdout=f)
        print(f" 임시 metadata.csv 생성 완료: {tmp_csv}")

        # 2. 썸네일 경로 준비
        thumbnail_path = os.path.join(scan_dir, "thumbnail", "thumb.jpg")
        has_thumbnail = os.path.exists(thumbnail_path)

        # 3. 읽고 썸네일 컬럼 추가하여 저장
        with open(tmp_csv, "r", encoding="utf-8") as fin, open(csv_path, "w", encoding="utf-8") as fout:
            lines = fin.readlines()
            if not lines:
                print(" exiftool 출력이 비어 있습니다.")
                return

            # 헤더 수정
            header = lines[0].strip() + ",thumbnail\n"
            fout.write(header)

            for line in lines[1:]:
                line = line.strip()
                thumb_col = thumbnail_path if has_thumbnail else ""
                fout.write(f"{line},{thumb_col}\n")

        print(f" 최종 metadata.csv 저장 완료: {csv_path}")
        os.remove(tmp_csv)

    except Exception as e:
        print(f"metadata.csv 생성 중 에러: {e}")

        