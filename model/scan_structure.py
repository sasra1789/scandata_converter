import os

def create_scan_structure(base_path, seq, shot, version="v001"):
    """
    지정된 경로 하위에 스캔 폴더 구조를 생성한다.
    /base_path/seq/shot/plate/version/org ... 형태
    """
    shot_root = os.path.join(base_path, seq, shot, "plate", version)
    subfolders = ["org", "jpg", "mp4", "webm", "thumbnail", "montage"]
    
    for sub in subfolders:
        os.makedirs(os.path.join(shot_root, sub), exist_ok=True)

    # metadata 파일도 빈 채로 생성
    metadata_path = os.path.join(shot_root, "metadata.json")
    if not os.path.exists(metadata_path):
        with open(metadata_path, "w") as f:
            f.write("{}")
    
    return shot_root
