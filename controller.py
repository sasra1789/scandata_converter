# controller.py
# 버튼 이벤트 처리 
from model import  (excel_manager, converter)
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

# 썸넬생성1 ( 폴더 선택 후 첫 exr 파일을 찾음 )
def on_select_path(ui):
    # 폴더 선택
    folder = QFileDialog.getExistingDirectory(ui, "Select Scan Folder")
    if not folder:
        return

    ui.path_input.setText(folder)

    # =============================
    # 썸네일 생성 (첫 EXR 파일 기준)
    # =============================
    exr_files = [f for f in os.listdir(folder) if f.endswith(".exr")]
    if exr_files:
        first_exr = os.path.join(folder, exr_files[0])
        thumbnail_path = os.path.join(folder, "thumbnail", "thumb.jpg")
        convert_exr_to_jpg_single_frame_ffmpeg(first_exr, thumbnail_path)
        print(f"[썸네일] 생성 완료: {thumbnail_path}")
    else:
        print("[썸네일] EXR 파일이 없어 썸네일 생략")

    # =============================
    # 메타데이터 CSV 생성
    # =============================
    metadata_csv = os.path.join(folder, "metadata.csv")
    if not os.path.exists(metadata_csv):
        generate_metadata_csv(folder, metadata_csv)
        print(f"[메타데이터] 생성 완료: {metadata_csv}")
    else:
        print(f"[메타데이터] 기존 파일 사용: {metadata_csv}")

    # =============================
    # 테이블 로딩
    # =============================
    metadata = load_metadata_csv(metadata_csv)
    ui.populate_table(metadata)
    print(f"[UI] 테이블 데이터 로딩 완료")


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

