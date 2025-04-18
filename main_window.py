

from model.converter_controller import load_scan_data
# 파일 상단
from controller import on_excel_save

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QTableWidget, QTableWidgetItem,
    QCheckBox, QComboBox,  QFileDialog, QHeaderView
)
from PySide6.QtGui import QPixmap
import sys




class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shotgun: IO Manager")
        self.resize(1200, 700)

        # ===== 상단: 경로 + 버튼 + 옵션 =====
        self.path_input = QLineEdit()
        self.select_btn = QPushButton("Select")
        self.load_btn = QPushButton("Load")

        self.option_non_retime = QCheckBox("Non Retime")
        self.option_mov_to_dpx = QCheckBox("MOV to DPX")
        self.option_colorspace = QComboBox()
        self.option_colorspace.addItems(["rec709", "ACES", "Linear", "sRGB"])

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Path:"))
        top_layout.addWidget(self.path_input)
        top_layout.addWidget(self.select_btn)
        top_layout.addWidget(self.load_btn)
        top_layout.addWidget(self.option_non_retime)
        top_layout.addWidget(self.option_mov_to_dpx)
        top_layout.addWidget(QLabel("Colorspace:"))
        top_layout.addWidget(self.option_colorspace)

        # ===== 중간: 테이블 =====
        self.table = QTableWidget()
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "Check", "Thumbnail", "Roll", "Seq Name", "Shot Name", 
            "Version", "Type", "Scan Path", "Scan Name", "Clip Name",
            "Resolution", "FrameCount"
        ])

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # ===== 하단: Excel 경로 + 버튼들 =====
        # self.excel_label = QLabel("/home/rapa/westworld_serin/converter/scanlist_01.csv")
        # self.save_btn = QPushButton("Save")
        # self.edit_btn = QPushButton("Edit")
        # self.validate_btn = QPushButton("Validate")
        # self.collect_btn = QPushButton("Collect")
        # self.publish_btn = QPushButton("Publish")

        # ===== 엑셀 경로 라벨 =====
        self.excel_label = QLabel("/home/rapa/westworld_serin/converter/scanlist_01.csv")

        # ===== Excel 버튼 =====
        self.save_btn = QPushButton(" Excel Save")
        self.edit_btn = QPushButton("Excel Edit")
        excel_btn_layout = QHBoxLayout()
        excel_btn_layout.addWidget(self.save_btn)
        excel_btn_layout.addWidget(self.edit_btn)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.excel_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.save_btn)
        bottom_layout.addWidget(self.edit_btn)

        # bottom_layout.addWidget(self.collect_btn)
        # bottom_layout.addWidget(self.publish_btn)

        # 엑셀 세이브 버튼 
        self.save_btn.clicked.connect(lambda: on_excel_save(self))


        # ===== 메인 레이아웃 =====
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.table)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

        # 연결 (예시)
        self.select_btn.clicked.connect(self.select_path)


        # load 버튼 연결
        self.load_btn.clicked.connect(self.on_load_clicked)

    def select_path(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Scan Folder")
        if folder:
            self.path_input.setText(folder)
            # TODO: load logic
        
    
    # 썸네일 추가
    def create_thumbnail_widget(image_path, size=(80, 45)):
        label = QLabel()
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(size[0], size[1])
            label.setPixmap(pixmap)
        else:
            label.setText("[이미지 없음]")
        return label
    
    def create_checkbox_widget(checked=True):
        checkbox = QCheckBox()
        checkbox.setChecked(checked)
        return checkbox
    
    

    # 로드했을 때
    def on_load_clicked(self, create_thumbnail_widget, create_checkbox_widget):
        folder = self.path_input.text()
        scan_data = load_scan_data(folder)
        self.populate_table(scan_data)

        self.table.setRowCount(len(scan_data))
        for row, item in enumerate(scan_data):
            # 0. Check
            checkbox = create_checkbox_widget()
            self.table.setCellWidget(row, 0, checkbox)

            # 1. Thumbnail
            thumb_widget = create_thumbnail_widget(item["thumbnail"])
            self.table.setCellWidget(row, 1, thumb_widget)

            # 2. Roll
            roll_item = QTableWidgetItem("Roll")
            roll_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable)
            self.table.setItem(row, 2, roll_item)

            # 3. Seq Name
            seq_item = QTableWidgetItem("Sequence")
            seq_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable)
            self.table.setItem(row, 3, seq_item)

            # 4. Shot Name
            shot_item = QTableWidgetItem(item["shot_name"])
            shot_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable)
            self.table.setItem(row, 4, shot_item)

            # 5. Version
            ver_item = QTableWidgetItem(item["version"])
            ver_item.setFlags(Qt.ItemIsEnabled)
            self.table.setItem(row, 5, ver_item)

            # 6. Type
            type_item = QTableWidgetItem("exr")
            type_item.setFlags(Qt.ItemIsEnabled)
            self.table.setItem(row, 6, type_item)

            # 7. Scan Path
            path_item = QTableWidgetItem(item["path"])
            path_item.setFlags(Qt.ItemIsEnabled)
            self.table.setItem(row, 7, path_item)

            # 8. Scan Name
            scan_item = QTableWidgetItem("")
            scan_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable)
            self.table.setItem(row, 8, scan_item)

            # 9. Clip Name
            clip_item = QTableWidgetItem("")
            clip_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable)
            self.table.setItem(row, 9, clip_item)

        
    def populate_table(self, data: list[dict]):
        self.table.setRowCount(len(data))
        for row, item in enumerate(data):
            # 0. Check
            checkbox = QCheckBox()
            checkbox.setChecked(item.get("check", True))
            self.table.setCellWidget(row, 0, checkbox)

            # 1. Thumbnail
            thumb_widget = self.create_thumbnail_widget(item.get("thumbnail", ""))
            self.table.setCellWidget(row, 1, thumb_widget)

            # 2~9. 텍스트 셀
            for col, key in enumerate(["roll", "seq", "shot", "version", "type", "path", "scan", "clip"], start=2):
                cell = QTableWidgetItem(item.get(key, ""))
                editable_cols = [2, 3, 4, 8, 9]
                if col in editable_cols:
                    cell.setFlags(cell.flags() | Qt.ItemIsEditable)
                else:
                    cell.setFlags(Qt.ItemIsEnabled)
                self.table.setItem(row, col, cell)

    # 엑셀 데이터 가져옴 
    def get_table_data(self) -> list[dict]:
        data = []
        for row in range(self.table.rowCount()):
            row_data = {}

            # 0. Checkbox
            checkbox = self.table.cellWidget(row, 0)
            row_data["check"] = checkbox.isChecked() if checkbox else False

            # 1. Thumbnail (경로는 따로 저장한 경우만)
            # GUI용이라 패스, 또는 썸네일 경로 저장
            row_data["thumbnail"] = ""

            # 2~9. 텍스트 셀
            keys = [
                "roll", "seq_name", "shot_name", "version", "type",
                "scan_path", "scan_name", "clip_name", "resolution", "frame_count"
            ]
            for col, key in enumerate(keys, start=2):
                item = self.table.item(row, col)
                row_data[key] = item.text() if item else ""
            data.append(row_data)
        return data
    
    def update_shotnames(self, mapping):
        """
        엑셀에서 불러온 Shot/Seq 이름을 테이블에 반영
        mapping = {
            "scan_path": {
                "seq_name": ...,
                "shot_name": ...
            }
        }
        """
        for row in range(self.table.rowCount()):
            scan_path_item = self.table.item(row, 7)  # Scan Path 열
            if not scan_path_item:
                continue

            path = scan_path_item.text()
            if path in mapping:
                seq = mapping[path].get("seq_name", "")
                shot = mapping[path].get("shot_name", "")

                self.table.item(row, 3).setText(seq)   # Seq Name
                self.table.item(row, 4).setText(shot)  # Shot Name

        print(f"[UI] 엑셀 매핑 적용 완료")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())