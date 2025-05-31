import difflib
import json
import os

# Json 파일 로드
json_path = os.path.join(os.path.dirname(__file__), "..", "Json", "Subway_Station.json")
with open(json_path, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# DATA 키에서 필요한 정보만 추출하여 map 구성
SUBWAY_MAP = {}

for entry in raw_data:
    line = entry["line_name"]
    station = entry["station_name"]
    station_id = entry["station_id"]

    if line not in SUBWAY_MAP:
        SUBWAY_MAP[line] = {}       
    
    SUBWAY_MAP[line][station] = station_id

def get_subway_statn_id(station: str, line: str) -> str:
    """
    정확한 정류장 ID 반환 (직접 매핑)
    """
    return SUBWAY_MAP.get(line, {}).get(station)

def get_exact_statn_id(station: str, line: str) -> str:
    """
    정확히 일치하는 정류장 ID 반환 (오류 방지를 위해 별도 함수화)
    """
    return SUBWAY_MAP.get(line, {}).get(station)

def find_closest_station_name(station: str, line: str) -> str:
    """
    역 이름이 정확히 일치하지 않을 경우 가장 유사한 이름 반환
    """
    candidates = SUBWAY_MAP.get(line, {}).keys()
    best_match = difflib.get_close_matches(station, candidates, n=1)
    return best_match[0] if best_match else station

print("[DEBUG] SUBWAY_MAP type:", type(SUBWAY_MAP))
print("[DEBUG] First few keys in SUBWAY_MAP:", list(SUBWAY_MAP.keys())[:5])

