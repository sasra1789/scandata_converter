# controller.py
from model import  (excel_manager, converter)
                         # scan_loader, shotgrid_api)
from PySide6.QtWidgets import QFileDialog, QMessageBox, QTableWidgetItem, QCheckBox, QLabel
from model. excel_manager import save_to_excel
from model.scan_structure import create_scan_structure
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
    path = QFileDialog.getOpenFileName(ui, "Open Excel", filter="Excel Files (*.xls *.xlsx)")[0]
    if not path:
        return

    mapping = excel_manager.load_shotnames_from_excel(path)
    ui.update_shotnames(mapping)
    QMessageBox.information(ui, "Loaded", "엑셀에서 샷네임 불러오기 완료!")


def on_convert_clicked(ui):
    table_data = ui.get_table_data()
    for row in table_data:
        src = row["path"]
        shot = row["shot_name"]
        base_dir = f"/project/{row['seq_name']}/{shot}/plate/{row['version']}"

        converter.convert_exr_to_jpg(src, 
                                     f"{base_dir}/jpg")
        converter.create_mp4_from_jpgs(f"{base_dir}/jpg", 
                                       f"{base_dir}/mp4/{shot}_plate_{row['version']}.mp4")
        converter.create_webm_from_mp4(f"{base_dir}/mp4/{shot}_plate_{row['version']}.mp4", f"{base_dir}/webm")
        converter.generate_thumbnail(f"{base_dir}/jpg", f"{base_dir}/thumbnail")
        converter.generate_montage(f"{base_dir}/jpg", f"{base_dir}/montage")


def on_publish_clicked(ui):
    table_data = ui.get_table_data()
    for row in table_data:
        media = {
            "mp4": f"/project/{row['seq_name']}/{row['shot_name']}/plate/{row['version']}/mp4/{row['shot_name']}.mp4",
            "webm": f"/project/{row['seq_name']}/{row['shot_name']}/plate/{row['version']}/webm/{row['shot_name']}.webm",
            "thumbnail": f"/project/{row['seq_name']}/{row['shot_name']}/plate/{row['version']}/thumbnail/thumb.jpg"
        }
        shotgrid_api.upload_to_shotgrid(row, media)

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

