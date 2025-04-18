# controller.py
from model import  (excel_manager, converter)
                         # scan_loader, shotgrid_api)
from PySide6.QtWidgets import QFileDialog, QMessageBox, QTableWidgetItem, QCheckBox, QLabel
from model. excel_manager import save_to_excel
from model.scan_structure import create_scan_structure
from model.metadata_reader import extract_metadata_from_exr
from model.metadata_reader import save_metadata_csv  # 기존에 만든 csv 저장 함수
from PySide6.QtGui import QPixmap

def on_select_path(ui):
    folder = QFileDialog.getExistingDirectory(ui, "Select Scan Folder")
    if folder:
        ui.path_input.setText(folder)
        on_load_clicked(ui)

def on_load_clicked(ui):
    scan_dir = ui.path_input.text()
    exr_files = scan_loader.find_exr_files(scan_dir)

    data = []
    for exr_path in exr_files:
        shot_name = scan_loader.auto_generate_shot_name(exr_path)
        data.append({
            "thumbnail": "",  # 썸네일은 나중에 생성
            "roll": "", 
            "seq_name": "", 
            "shot_name": shot_name,
            "version": "v001",
            "type": "org",
            "path": exr_path,
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
# def on_excel_save(ui):
#     path = QFileDialog.getSaveFileName(ui, "Save Excel", filter="Excel Files (*.xls *.xlsx)")[0]
#     if not path:
#         return

#     table_data = ui.get_table_data()
#     excel_manager.save_to_excel(table_data, path)
#     QMessageBox.information(ui, "Success", "Excel 저장 완료!")


def on_excel_edit(ui):
    path = QFileDialog.getOpenFileName(ui, "Open Excel")[0]
    if not path:
        return

    mapping = excel_manager.load_shotnames_from_excel(path)

    for row in range(ui.table.rowCount()):
        scan_path = ui.table.item(row, 7).text()  # Scan Path 열
        shot_name = mapping.get(scan_path)
        if shot_name:
            item = QTableWidgetItem(shot_name)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            ui.table.setItem(row, 4, item)  # Shot Name 열

    QMessageBox.information(ui, "완료", "샷 이름이 엑셀에서 적용되었습니다.")

def on_convert_clicked(ui):
    table_data = ui.get_table_data()

    for row in table_data:
        seq = row["seq_name"]
        shot = row["shot_name"]
        version = row["version"]
        src = row["path"]

        # 📁 폴더 생성
        folder_paths = create_scan_structure("/project", seq, shot, version)
        shot_base_name = f"{shot}_plate_{version}"

        # 🎨 변환
        converter.convert_exr_to_jpg(src, folder_paths["jpg"])
        converter.create_mp4_from_jpgs(folder_paths["jpg"],
                                       os.path.join(folder_paths["mp4"], f"{shot_base_name}.mp4"))
        converter.create_webm_from_mp4(
            os.path.join(folder_paths["mp4"], f"{shot_base_name}.mp4"),
            folder_paths["webm"]
        )
        converter.generate_thumbnail(folder_paths["jpg"], folder_paths["thumbnail"])
        converter.generate_montage(folder_paths["jpg"], folder_paths["montage"])

        # 🧠 메타데이터 추출 및 저장
        metadata = extract_metadata_from_exr(src)
        if metadata:
            metadata_csv_path = os.path.join(folder_paths["org"], "..", "metadata.csv")
            save_metadata_csv(metadata, metadata_csv_path)
            print(f"[Metadata] 저장 완료: {metadata_csv_path}")

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

def populate_table(ui, data):
    ui.table.setRowCount(len(data))

    for row, item in enumerate(data):
        # 0. Check
        checkbox = QCheckBox()
        checkbox.setChecked(item.get("check", True))
        ui.table.setCellWidget(row, 0, checkbox)

        # 1. Thumbnail
        thumb_label = QLabel()
        pixmap = QPixmap(item.get("thumbnail", ""))
        if not pixmap.isNull():
            thumb_label.setPixmap(pixmap.scaled(80, 45))
        else:
            thumb_label.setText("No Image")
        ui.table.setCellWidget(row, 1, thumb_label)

        # 2~9. 나머지 셀들
        keys = ["roll", "seq_name", "shot_name", "version", "type",
                "scan_path", "scan_name", "clip_name"]

        for col, key in enumerate(keys, start=2):
            val = item.get(key, "")
            table_item = QTableWidgetItem(val)
            table_item.setFlags(table_item.flags() | Qt.ItemIsEditable)
            ui.table.setItem(row, col, table_item)

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
        keys = ["roll", "seq_name", "shot_name", "version", "type",
                "scan_path", "scan_name", "clip_name"]
        row_data = {"check": checked, "thumbnail": thumbnail_path}

        for col, key in enumerate(keys, start=2):
            item = ui.table.item(row, col)
            row_data[key] = item.text() if item else ""

        data.append(row_data)

    return data

