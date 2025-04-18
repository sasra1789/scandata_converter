# 엑셀 저장 함수 
import openpyxl
from openpyxl.styles import Alignment
from openpyxl import Workbook

def save_to_excel(data_list, path):
    """
    UI 테이블 데이터를 Excel 파일로 저장
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "ScanData"

    headers = [
        "Roll", "Seq Name", "Shot Name", "Version",
        "Resolution", "FrameCount",
        "Scan Path", "Clip Name"
    ]
    ws.append(headers)

    for row in data_list:
        ws.append([
            row.get("roll", ""),
            row.get("seq_name", ""),
            row.get("shot_name", ""),
            row.get("version", ""),
            row.get("resolution", ""),
            row.get("frame_count", ""),
            row.get("scan_path", ""),
            row.get("clip_name", "")
        ])

    # 헤더 bold 처리
    for cell in ws[1]:
        cell.font = Font(bold=True)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    wb.save(path)
    print(f"[Excel] 저장 완료: {path}")

    

def load_shotnames_from_excel(path):
    """
    PM이 편집한 Excel 파일에서 Shot Name / Seq Name을 다시 불러옴
    """
    wb = openpyxl.load_workbook(path)
    ws = wb.active

    mapping = {}

    for row in ws.iter_rows(min_row=2, values_only=True):
        scan_path = row[6]  # Scan Path 열
        shot_name = row[2]  # Shot Name 열
        seq_name = row[1]   # Seq Name 열

        if scan_path:
            mapping[scan_path] = {
                "shot_name": shot_name,
                "seq_name": seq_name
            }

    print(f"[Excel] 불러온 샷 매핑: {len(mapping)}개")
    return mapping