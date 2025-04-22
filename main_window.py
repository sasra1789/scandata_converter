# UI 구성


from model.converter import load_scan_data
from controller import on_select_path
# 파일 상단
from controller import on_excel_save

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QTableWidget, QTableWidgetItem,
    QCheckBox, QComboBox,  QFileDialog, QHeaderView
)
from PySide6.QtGui import QPixmap
import os
import sys




class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shotgun: IO Manager")
        self.resize(1200, 700)


        # ===== 상단: 경로 + 버튼 + 옵션 =====
        self.path_input = QLineEdit()
        self.select_btn = QPushButton("Select")


        self.option_non_retime = QCheckBox("Non Retime")
        self.option_mov_to_dpx = QCheckBox("MOV to DPX")
        self.option_colorspace = QComboBox()
        self.option_colorspace.addItems(["rec709", "ACES", "Linear", "sRGB"])

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Path:"))
        top_layout.addWidget(self.path_input)
        top_layout.addWidget(self.select_btn)
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
        self.save_btn = QPushButton("Excel Save")
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
        self.save_btn.clicked.connect(lambda: on_excel_save(self)) # 클릭할 때 실행하게 하려면 lambda로 감싸야함 


        # ===== 메인 레이아웃 =====
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.table)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

        # 연결 (예시)
        self.select_btn.clicked.connect(lambda: on_select_path(self)) # 클릭할 때 실행하게 하려면 lambda로 감싸야함


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
    
    

    def populate_table(self, data):
        """
        썸네일 이미지를 Thumbnail 열 (0번째 열)에 실제 이미지로 표시
        """
        self.table.setRowCount(len(data))
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Thumbnail", "File Name", "Width", "Height", "Directory", "Lens"
        ])

        for row, item in enumerate(data):
            # 0. 썸네일 경로 생성
            thumb_path = os.path.join("thumbnail", "thumb.jpg")

            # 썸네일 QLabel 생성
            thumb_label = QLabel()
            pixmap = QPixmap(thumb_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(80, 45)  # 사이즈는 자유 조절
                thumb_label.setPixmap(pixmap)
            else:
                thumb_label.setText("No Image")

            self.table.setCellWidget(row, 0, thumb_label)

            # 나머지 텍스트 셀들
            self.table.setItem(row, 1, QTableWidgetItem(item.get("FileName", "")))
            self.table.setItem(row, 2, QTableWidgetItem(item.get("ImageWidth", "")))
            self.table.setItem(row, 3, QTableWidgetItem(item.get("ImageHeight", "")))
            self.table.setItem(row, 4, QTableWidgetItem(item.get("Directory", "")))
            self.table.setItem(row, 5, QTableWidgetItem(item.get("FocalLength35efl", "")))

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