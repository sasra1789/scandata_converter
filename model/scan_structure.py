# 폴더구조 자동생성
import os

def create_scan_structure(root_dir, sequence, shot, version):
    """
    전체 plate 폴더 구조를 생성하고, 생성된 경로를 dict로 반환

    Parameters:
        root_dir (str): /project
        sequence (str): S030
        shot (str): S030_A0030
        version (str): v001

    Returns:
        dict: {
            "base": ..., "org": ..., "jpg": ..., ...
        }
    """

    base_path = os.path.join(root_dir, sequence, shot, "plate", version)
    subdirs = ["org", "jpg", "mp4", "webm", "thumbnail", "montage"]
    created_paths = {"base": base_path}

    for sub in subdirs:
        path = os.path.join(base_path, sub)
        os.makedirs(path, exist_ok=True)
        created_paths[sub] = path

    print(f"[폴더 생성] {base_path} 구조 생성 완료")
    return created_paths
