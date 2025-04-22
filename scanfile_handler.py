# .exr 또는 .mov 등 파일을 스캔하여 리스트로 반환하는 유틸리티성 파일 
# model/scanfile_handler.py
import os
import pyseq

def find_exr_sequences(folder_path):
    """
    pyseq를 이용해 EXR 시퀀스를 자동으로 묶어 리턴
    """
    all_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(".exr")]
    sequences = pyseq.get_sequences(all_files)

    result = []
    for seq in sequences:
        result.append({
            "dir": seq.dirname(),
            "basename": seq.basename(),
            "padding": seq.padding(),    # ex: %04d
            "start": seq.start(),
            "end": seq.end(),
            "length": seq.length(),
            "sample": seq[0].path        # 대표 프레임 경로 (썸네일용)
        })
    return result
