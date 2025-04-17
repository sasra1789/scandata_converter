# controller.py
from model import scan_loader, excel_manager, converter, shotgrid_api
from PySide6.QtWidgets import QFileDialog, QMessageBox

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


def on_excel_save(ui):
    path = QFileDialog.getSaveFileName(ui, "Save Excel", filter="Excel Files (*.xls *.xlsx)")[0]
    if not path:
        return

    table_data = ui.get_table_data()
    excel_manager.save_to_excel(table_data, path)
    QMessageBox.information(ui, "Success", "Excel 저장 완료!")


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
