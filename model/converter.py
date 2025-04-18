# 📁 model/converter.py
import os
import cv2
import imageio
import subprocess

def convert_exr_to_jpg(src_path, dst_path):
    """
    EXR 파일을 JPG로 변환 (전체 시퀀스용)
    """
    img = imageio.imread(src_path)
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    imageio.imwrite(dst_path, img)
    print(f"[JPG] 변환 완료: {dst_path}")

def convert_exr_to_jpg_single_frame_ffmpeg(exr_path: str, jpg_path: str):
    """
    ffmpeg를 이용해 EXR 단일 프레임을 썸네일용 JPG로 변환
    """
    os.makedirs(os.path.dirname(jpg_path), exist_ok=True)

    command = [
        "ffmpeg", "-y",
        "-i", exr_path,
        "-frames:v", "1",
        "-q:v", "2",
        jpg_path
    ]
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[FFMPEG] 썸네일 생성 완료: {jpg_path}")
    except subprocess.CalledProcessError:
        print(f"[FFMPEG] 변환 실패: {exr_path}")

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
