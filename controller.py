# controller.py
from model import  (excel_manager, converter)
                         # scan_loader, shotgrid_api)
from PySide6.QtWidgets import QFileDialog, QMessageBox, QTableWidgetItem, QCheckBox, QLabel
from model.excel_manager import save_to_excel
from model.scan_structure import create_scan_structure
from model.metadata_reader import (extract_metadata_from_exr, save_metadata_csv , generate_metadata_csv,
                                                load_metadata_csv)
from scanfile_handler import find_exr_sequences
from model.converter import convert_exr_to_jpg_single_frame_ffmpeg
# from main_window import create_thumbnail_widget
from PySide6.QtGui import QPixmap
import os


def extract_first_exr_path(folder):
    exr_list = [f for f in os.listdir(folder) if f.endswith(".exr")]
    if not exr_list:
        return None
    return os.path.join(folder, exr_list[0])

# 썸넬생성
def on_select_path(ui):
    folder = QFileDialog.getExistingDirectory(ui, "Select Scan Folder")
    if folder:
        ui.path_input.setText(folder)

        # 1. 썸네일 생성
        exr_files = [f for f in os.listdir(folder) if f.endswith(".exr")]
        if exr_files:
            exr_path = os.path.join(folder, exr_files[0])
            thumb_path = os.path.join(folder, "thumbnail", "thumb.jpg")
            convert_exr_to_jpg_single_frame_ffmpeg(exr_path, thumb_path)

        # 2. metadata 생성
        csv_path = os.path.join(folder, "metadata.csv")
        if not os.path.exists(csv_path):
            generate_metadata_csv(folder, csv_path)

        # 3. 테이블 로딩
        data = load_metadata_csv(csv_path)
        ui.populate_table(data)

def on_load_clicked(ui):
    # scan_dir = 폴더선택창에서 고른 경로 
    scan_dir = ui.path_input.text()
    sequences = find_exr_sequences(scan_dir)
    data = []
    for seq in sequences:
        # 시퀀스 베이스로 shot 이름 생성 (PM이 이후 엑셀에서 수정 가능)
        shot_name = seq['basename']

        # 썸네일은 시퀀스의 첫 프레임으로 사용
        thumbnail = seq['sample']

        data.append({
            "thumbnail": thumbnail,
            "roll": "", 
            "seq_name": "", 
            "shot_name": shot_name,
            "version": "v001",
            "type": "org",
            "path": seq['dir'],       # 폴더 경로만 저장 (시퀀스 단위)
            "scan_name": "",
            "clip_name": ""
        })


    ui.populate_table(data)


# 엑셀 저장기능 
def on_save_clicked(ui):
    data = ui.get_table_data()
    path = ui.excel_label.text()
    save_to_excel(data, path)
    print(f"[Excel] 저장 완료: {path}")


# save 버튼 연결
def on_excel_save(main_window):
    data = main_window.get_table_data()
    excel_path = main_window.excel_label.text()
    save_to_excel(data, excel_path)


def on_excel_edit(ui):
    path = QFileDialog.getOpenFileName(ui, "Open Excel")[0]
    if not path:
        return

    mapping = excel_manager.load_shotnames_from_excel(path)
    ui.update_shotnames(mapping)
    QMessageBox.information(ui, "Loaded", "엑셀에서 샷네임 불러오기 완료!")

   
    mapping = excel_manager.load_shotnames_from_excel(path)
    ui.update_shotnames(mapping)
    QMessageBox.information(ui, "Loaded", "엑셀에서 샷네임 불러오기 완료!")


def on_convert_clicked(ui):
    table_data = ui.get_table_data()

    for row in table_data:
        # 기본 값 추출
        seq = row["seq_name"]
        shot = row["shot_name"]
        version = row["version"]
        src = row["path"]

        # 1️ 폴더 자동 생성
        base_paths = create_scan_structure("/project", seq, shot, version)
        shot_base = f"{shot}_plate_{version}"

        # 2 변환 처리
        converter.convert_exr_to_jpg_single_frame_ffmpeg(src, base_paths["jpg"])
        converter.create_mp4_from_jpgs(base_paths["jpg"],
            os.path.join(base_paths["mp4"], f"{shot_base}.mp4"))
        converter.create_webm_from_mp4(
            os.path.join(base_paths["mp4"], f"{shot_base}.mp4"),
            base_paths["webm"])
        converter.generate_thumbnail(base_paths["jpg"], base_paths["thumbnail"])
        converter.generate_montage(base_paths["jpg"], base_paths["montage"])

        # 3️ 메타데이터 추출 및 저장
        metadata = extract_metadata_from_exr(src)
        if metadata:
            metadata_path = os.path.join(base_paths["base"], "metadata.csv")
            save_metadata_csv(metadata, metadata_path)
            print(f"[Metadata] 저장 완료: {metadata_path}")

            # UI 테이블에 resolution / frame count 셀 채우기
            for row_idx in range(ui.table.rowCount()):
                path_item = ui.table.item(row_idx, 7)
                if path_item and path_item.text() == src:
                    res_item = ui.table.item(row_idx, 10)
                    frame_item = ui.table.item(row_idx, 11)

                    if res_item:
                        res_item.setText(metadata.get("Resolution", ""))
                    if frame_item:
                        frame_item.setText(str(metadata.get("FrameCount", "")))



def on_publish_clicked(ui):
    table_data = ui.get_table_data()

    for row in table_data:
        seq = row["seq_name"]
        shot = row["shot_name"]
        version = row["version"]

        folder_paths = create_scan_structure("/project", seq, shot, version)
        shot_base_name = f"{shot}_plate_{version}"

        # 미디어 경로 구성
        media = {
            "mp4": os.path.join(folder_paths["mp4"], f"{shot_base_name}.mp4"),
            "webm": os.path.join(folder_paths["webm"], f"{shot_base_name}.webm"),
            "thumbnail": os.path.join(folder_paths["thumbnail"], "thumb.jpg")
        }

        # 샷 정보 전달 (추후 ShotGrid 등록용)
        shot_info = {
            "seq_name": seq,
            "shot_name": shot,
            "version": version,
            "scan_path": row["path"]
            # 필요하면 metadata도 추가 가능
        }

        # ShotGrid 등록 요청
        # (아직 구현되지 않은 shotgrid_api.upload_to_shotgrid()에 연결됨)
        shotgrid_api.upload_to_shotgrid(shot_info, media)


# 데이터 추출함수     
def get_table_data(ui):
    data = []
    row_count = ui.table.rowCount()

    for row in range(row_count):
        # 0. 체크박스 상태
        checkbox = ui.table.cellWidget(row, 0)
        checked = checkbox.isChecked() if checkbox else False

        # 1. 썸네일 (생략 가능 - 저장 필요 없으면)
        thumb_label = ui.table.cellWidget(row, 1)
        thumbnail_path = thumb_label.pixmap().cacheKey() if thumb_label else ""

        # 2~9. 텍스트 셀들
        keys = ["roll", "seq_name", "shot_name", "version", "Filetype",
                "scan_path", "scan_name", "clip_name"]
        row_data = {"check": checked, "thumbnail": thumbnail_path}

        for col, key in enumerate(keys, start=2):
            item = ui.table.item(row, col)
            row_data[key] = item.text() if item else ""

        data.append(row_data)

    return data

