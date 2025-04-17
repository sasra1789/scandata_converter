# 📁 model/converter.py
import imageio
import os
import cv2

def convert_exr_to_jpg(src_path, dst_path):
    img = imageio.imread(src_path)
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    imageio.imwrite(dst_path, img)


def create_mp4_from_jpgs(jpg_dir, dst_path):
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


def create_webm_from_mp4(mp4_path, dst_path):
    cmd = f"ffmpeg -y -i {mp4_path} -c:v libvpx -b:v 1M {dst_path}"
    os.system(cmd)


def generate_thumbnail(jpg_dir, dst_path):
    jpg_files = sorted([f for f in os.listdir(jpg_dir) if f.endswith(".jpg")])
    if jpg_files:
        first = os.path.join(jpg_dir, jpg_files[0])
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        imageio.imwrite(dst_path, imageio.imread(first))


def generate_montage(jpg_dir, dst_path):
    jpg_files = sorted([f for f in os.listdir(jpg_dir) if f.endswith(".jpg")])[:5]
    images = [cv2.imread(os.path.join(jpg_dir, f)) for f in jpg_files]
    montage = cv2.hconcat(images)
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    cv2.imwrite(dst_path, montage)
