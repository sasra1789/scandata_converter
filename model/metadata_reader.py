import csv
import os

def save_metadata_csv(metadata_dict, save_path):
    """
    메타데이터 딕셔너리를 CSV 형식으로 저장합니다.

    Parameters:
        metadata_dict (dict): {"key": value, ...}
        save_path (str): 저장할 csv 파일 경로
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    with open(save_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Key", "Value"])
        for key, value in metadata_dict.items():
            writer.writerow([key, value])

    return save_path



# metadata_reader.py

import subprocess

def extract_metadata_from_exr(filepath: str) -> dict:
    """
    exiftool을 이용해 EXR 파일의 메타데이터를 추출하고 딕셔너리로 반환합니다.
    리눅스에서만 동작합니다.
    """
    try:
        # exiftool 실행
        result = subprocess.run(
            ["exiftool", filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            print(f"[Error] exiftool 실패: {result.stderr}")
            return {}

        metadata = {}
        for line in result.stdout.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()

        # 필요한 주요 키만 추출해서 리네이밍
        simplified = {
            "Resolution": f"{metadata.get('Image Width')}x{metadata.get('Image Height')}",
            "FrameCount": metadata.get("Image Size"),  # 또는 프레임 카운트 추정값
            "Camera": metadata.get("Camera Model Name"),
            "Lens": metadata.get("Lens"),
            "Date": metadata.get("Create Date") or metadata.get("Date/Time Original"),
        }

        # 빈 값 제거
        return {k: v for k, v in simplified.items() if v}

    except Exception as e:
        print(f"[Error] 메타데이터 추출 실패: {e}")
        return {}


# 예시 실행
example_metadata = {
    "Resolution": "1920x1080",
    "FrameCount": 120,
    "Camera": "ALEXA LF",
    "Date": "2024-06-15",
    "Lens": "35mm"
}




save_metadata_csv(example_metadata, "/mnt/data/sample_metadata.csv")
