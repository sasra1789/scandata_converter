# 📁 model/converter.py
import os
import cv2
import imageio
import subprocess
from scanfile_handler import find_exr_sequences


# 썸넬생성2 (ffmpeg으로 exr -> jpg 변환) 
def convert_exr_to_jpg_single_frame_ffmpeg(src_exr, dst_jpg):
    """
    EXR 파일의 첫 프레임을 썸네일용 JPG로 변환
    ffmpeg를 사용하여 1프레임만 추출합니다.
    """

    # 1 출력 경로 디렉토리 생성
    os.makedirs(os.path.dirname(dst_jpg), exist_ok=True)

    # 2 ffmpeg 명령어 구성
    command = [
        "ffmpeg", "-y",               # 기존 파일 덮어쓰기
        "-i", src_exr,                # 입력 EXR
        "-frames:v", "1",             # 첫 프레임만 추출
        "-q:v", "2",                  # 높은 품질 JPG
        dst_jpg                       # 출력 JPG 경로
    ]

    #  명령 실행
    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f" [FFMPEG] 썸네일 생성 완료: {dst_jpg}")

    except subprocess.CalledProcessError as e:
        print(f" [FFMPEG] 변환 실패: {src_exr}")
        print(f"↳ 오류 메시지: {e}")

def create_mp4_from_jpgs(jpg_dir, dst_path):
    """
    JPG 시퀀스를 mp4로 변환 (OpenCV 사용)
    """
    jpg_files = sorted([f for f in os.listdir(jpg_dir) if f.endswith(".jpg")])
    if not jpg_files:
        return

    height, width, _ = cv2.imread(os.path.join(jpg_dir, jpg_files[0])).shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(dst_path, fourcc, 24.0, (width, height))

    for jpg in jpg_files:
        frame = cv2.imread(os.path.join(jpg_dir, jpg))
        out.write(frame)
    out.release()
    print(f"[MP4] 생성 완료: {dst_path}")

def create_webm_from_mp4(mp4_path, dst_path):
    """
    mp4 파일을 webm 포맷으로 변환 (ffmpeg 사용)
    """
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    cmd = f"ffmpeg -y -i {mp4_path} -c:v libvpx -b:v 1M {dst_path}"
    os.system(cmd)
    print(f"[WEBM] 생성 완료: {dst_path}")

def generate_thumbnail(jpg_dir, dst_path):
    """
    JPG 디렉토리에서 첫 프레임으로 썸네일 생성
    """
    jpg_files = sorted([f for f in os.listdir(jpg_dir) if f.endswith(".jpg")])
    if jpg_files:
        first = os.path.join(jpg_dir, jpg_files[0])
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        imageio.imwrite(dst_path, imageio.imread(first))
        print(f"[Thumbnail] 저장 완료: {dst_path}")

def generate_montage(jpg_dir, dst_path):
    """
    JPG 5장을 나란히 이어붙여 몽타주 이미지 생성
    """
    jpg_files = sorted([f for f in os.listdir(jpg_dir) if f.endswith(".jpg")])[:5]
    images = [cv2.imread(os.path.join(jpg_dir, f)) for f in jpg_files if cv2.imread(os.path.join(jpg_dir, f)) is not None]
    if not images:
        print("[Montage] 이미지 없음")
        return

    montage = cv2.hconcat(images)
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    cv2.imwrite(dst_path, montage)
    print(f"[Montage] 저장 완료: {dst_path}")

def load_scan_data(folder_path):
    """EXR 파일을 기반으로 테이블에 보여줄 데이터를 구성"""
    file_list = find_exr_sequences(folder_path)
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
