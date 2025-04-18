
import os
import subprocess
# import pandas as pd

def save_metadata_csv(data, project_root, shot_name, version, episode=None):
    """
    plate 버전 디렉토리에 metadata.csv 자동 저장

    Args:
        data (list[dict]): 저장할 메타데이터 (딕셔너리 리스트)
        project_root (str): 프로젝트 루트 경로 (/home/rapa/westworld_serin)
        shot_name (str): 샷 이름 (예: S030_0100)
        version (str): plate 버전 (예: v001)
        episode (str, optional): 에피소드 (예: EP01), 없으면 생략
    """
    # 시퀀스 이름 추출
    sequence_name = shot_name.split("_")[0]

    # 경로 조합
    base_path = os.path.join(project_root, "seq")
    if episode:
        base_path = os.path.join(base_path, episode)

    plate_path = os.path.join(
        base_path,
        sequence_name,
        shot_name,
        "plate",
        version
    )

    # 디렉토리 생성
    os.makedirs(plate_path, exist_ok=True)

    # 저장 경로
    save_path = os.path.join(plate_path, "metadata.csv")

    # 저장
    df = pd.DataFrame(data)
    df.to_csv(save_path, index=False)

    print(f"metadata 저장 완료: {save_path}")


# exif tool 을 이용하여 .exr 파일의 메타데이터 추출 
def extract_metadata_from_exr(filepath: str) -> dict:
    """
    exiftool을 이용해 EXR 파일의 메타데이터를 추출하고 딕셔너리로 반환합니다.
    리눅스에서만 동작합니다.
    """
    try:
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
            "FrameCount": metadata.get("Frame Count") or metadata.get("Image Size"),
            "Camera": metadata.get("Camera Model Name"),
            "Lens": metadata.get("Lens"),
            "Date": metadata.get("Create Date") or metadata.get("Date/Time Original"),
        }

        return {k: v for k, v in simplified.items() if v}

    except Exception as e:
        print(f"[Error] 메타데이터 추출 실패: {e}")
        return {}
