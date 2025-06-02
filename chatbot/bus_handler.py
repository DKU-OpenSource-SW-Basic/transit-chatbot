import csv
import json
import requests
import difflib
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Tuple, Optional
import urllib.parse
import pandas as pd
import subprocess
import shlex

# API KEY
SEOUL_SERVICE_KEY    = "1sq/rwVIQUlj/pGMERuN6nx+n6RE4Ioxf5ymfzg2LZgyne97Ex0Bmm4xBJ8jPFPHfFBhAOuXc///yNimFMb0jg=="
GYEONGGI_SERVICE_KEY = "cLnyMQHDF8fbs1XyKC1w2N6zZKMFCEFsvyiGh5IQYuEyMeU8JQ3Hf8XNmPgYxBuWKLBYdQIkcKOHmobGMlEdDw%3D%3D"

# 경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_DIR  = BASE_DIR / "csv"
JSON_DIR = BASE_DIR / "Json"

CAPITAL_STOP_CSV     = CSV_DIR / "capital_bus_stops.csv"
GYEONGGI_ROUTE_CSV   = CSV_DIR / "gyeonggi_bus_route.csv"
BUS_ROUTE_ID_JSON    = JSON_DIR / "busRouteId.json"

# 서울 노선 ID 매핑
with open(BUS_ROUTE_ID_JSON, encoding="utf-8") as f:
    seoul_route_map = {item["transport_name"]: item["transport_id"] for item in json.load(f)["DATA"]}

# CSV 로드
bus_stops = pd.read_csv(CAPITAL_STOP_CSV, encoding="utf-8")
gyeonggi_routes = pd.read_csv(GYEONGGI_ROUTE_CSV, encoding="utf-8")

# 정류장명 후보 리스트(서울/경기 전체)
all_stop_names = set(bus_stops['정류소명'].dropna().unique())

def similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_best_stop_name(query: str, candidates: List[str], threshold=0.4) -> str:
    matches = difflib.get_close_matches(query, candidates, n=1, cutoff=threshold)
    return matches[0] if matches else query

def get_seoul_arrival(route_no: str, station_name: str, top_n: int = 2) -> List[str]:
    route_id = seoul_route_map.get(route_no)
    if not route_id:
        return []
    
    url = "http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRouteAll"
    params = {"serviceKey": SEOUL_SERVICE_KEY, "busRouteId": route_id}
    try:
        resp = requests.get(url, params=params, timeout=5)
        root = ET.fromstring(resp.content)
        items = root.findall(".//itemList")

        results = []
        seen_plates = set()
        level_map = {"0": "정보 없음", "3": "여유", "4": "보통", "5": "혼잡"}

        # 유사한 정류장 top_n개 추출
        candidate_names = list(bus_stops['정류소명'].dropna().unique())
        scored = sorted(
            [(similarity(station_name, name), name) for name in candidate_names],
            reverse=True
        )
        selected_names = [name for score, name in scored if score >= 0.5][:top_n]

        # 해당 정류소들에 대해 모두 도는 구조
        node_ars_pairs = []
        for name in selected_names:
            nodes = bus_stops[bus_stops['정류소명'] == name]
            node_ids = set(str(x) for x in nodes['NODE_ID'].dropna().unique())
            ars_ids  = set(str(x) for x in nodes['ARS_ID'].dropna().unique())
            node_ars_pairs.append((name, node_ids, ars_ids))
        
        for item in items:
            item_ars_id = item.findtext("arsId")
            item_node_id = item.findtext("stId")
            matched_name = None
            for name, node_ids, ars_ids in node_ars_pairs:
                if (item_node_id in node_ids) or (item_ars_id in ars_ids):
                    matched_name = name
                    break
            if not matched_name:
                continue

            for i, label in [(1, ""), (2, "다음 ")]:
                plate_no = item.findtext(f"plainNo{i}") or item.findtext(f"vehId{i}") or ""
                arrmsg = item.findtext(f"arrmsg{i}") or "정보 없음"
                remain_code = item.findtext(f"reride_Num{i}")
                remain_level = level_map.get(str(remain_code), "정보 없음")
                if arrmsg == "정보 없음" and (remain_code is None or remain_code == "-1"):
                    continue
                # plate_no 중복 제거, 최대 4개까지
                if plate_no and plate_no not in seen_plates and len(results) < 4:
                    seen_plates.add(plate_no)
                    # [정류소명]도 같이 표기 가능 (선택)
                    results.append(f"[서울] {route_no} {label}버스({plate_no}): {arrmsg} / 혼잡도: {remain_level}")
        return results
    except Exception as e:
        return []


def get_gyeonggi_route_id(route_no: str) -> Optional[str]:
    matches = gyeonggi_routes[gyeonggi_routes["노선번호"] == route_no]
    return str(matches.iloc[0]["노선ID"]) if not matches.empty else None

def get_gyeonggi_arrival_by_route_with_curl(route_no: str, station_name: str) -> List[str]:
    route_id = get_gyeonggi_route_id(route_no)
    if not route_id:
        return []

    list_url = (
        f"https://apis.data.go.kr/6410000/busrouteservice/v2/getBusRouteStationListv2"
        f"?serviceKey={GYEONGGI_SERVICE_KEY}&routeId={route_id}&format=json"
    )
    try:
        command_list = shlex.split(f"curl -k '{list_url}'")
        process_list = subprocess.Popen(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_list, _ = process_list.communicate()

        if process_list.returncode != 0:
            return []

        try:
            data_list = json.loads(stdout_list)
            station_list = data_list.get("response", {}).get("msgBody", {}).get("busRouteStationList", [])
        except json.JSONDecodeError:
            return []

        # 유사도 상위 2개
        scored_stations = []
        min_similarity_threshold = 0.5
        for station in station_list:
            name = station.get("stationName")
            if name:
                score = similarity(station_name, name)
                if score >= min_similarity_threshold:
                    scored_stations.append((score, station))
        scored_stations.sort(reverse=True, key=lambda x: x[0])
        matching_stations = [x[1] for x in scored_stations[:2]]

        results = []
        seen_plates = set()
        for station in matching_stations:
            stop_id = station.get("stationId")
            stop_name = station.get("stationName")
            if not stop_id:
                continue

            arrival_url = (
                f"https://apis.data.go.kr/6410000/busarrivalservice/v2/getBusArrivalItemv2"
                f"?serviceKey={GYEONGGI_SERVICE_KEY}&stationId={stop_id}&routeId={route_id}&format=json"
            )
            command_arrival = shlex.split(f"curl -k '{arrival_url}'")
            process_arrival = subprocess.Popen(command_arrival, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_arrival, _ = process_arrival.communicate()
            if process_arrival.returncode != 0:
                continue
            try:
                data_arrival = json.loads(stdout_arrival)
                arrival_item = data_arrival.get("response", {}).get("msgBody", {}).get("busArrivalItem")
                if arrival_item:
                    crowded_map = {
                        "0": "정보 없음",
                        "1": "여유",
                        "2": "보통",
                        "3": "혼잡",
                        "4": "매우 혼잡"
                    }
                    seat_route_types = {
                        11, 12, 14, 16, 17, 21, 22, 41, 42, 51, 52
                    }
                    def format_remain_seat(remain, route_type):
                        if route_type in seat_route_types:
                            if remain is None or remain == -1:
                                return "정보 없음"
                            try:
                                remain = int(remain)
                                if remain == 0:
                                    return "만석"
                                return f"{remain}석"
                            except:
                                return "정보 없음"
                        else:
                            return "-"

                    route_type = int(arrival_item.get("routeTypeCd", 0))
                    count_this_station = 0
                    for i in [1, 2]:
                        plate_no = arrival_item.get(f"plateNo{i}")
                        predict_time = arrival_item.get(f"predictTime{i}")
                        remain_seat = arrival_item.get(f"remainSeatCnt{i}")
                        crowded_code = str(arrival_item.get(f"crowded{i}", "0"))
                        crowded_text = crowded_map.get(crowded_code, "정보 없음")
                        remain_text = format_remain_seat(remain_seat, route_type)
                        if plate_no and predict_time and str(predict_time).isdigit():
                            if plate_no not in seen_plates:
                                seen_plates.add(plate_no)
                                label = "다음 버스" if i == 2 else "버스"
                                info_str = (
                                    f"[경기] {route_no} {label}({plate_no}) [{stop_name}]: "
                                    f"{predict_time}분 / 잔여좌석: {remain_text} / 혼잡도: {crowded_text}"
                                )
                                results.append(info_str)
                                count_this_station += 1
                        if count_this_station >= 2:
                            break
                    if len(results) >= 4:
                        return results
            except json.JSONDecodeError:
                continue
        return results
    except Exception as e:
        return []

def deduplicate_and_limit(seoul_results: List[str], gyeonggi_results: List[str], max_total=4) -> List[str]:
    import re
    seen_plates = set()
    all_results = []
    for r in (seoul_results or []) + (gyeonggi_results or []):
        match = re.search(r'\(([^)]+)\)', r)
        plate_no = match.group(1) if match else None
        if plate_no and plate_no not in seen_plates:
            seen_plates.add(plate_no)
            all_results.append(r)
        elif not plate_no:
            all_results.append(r)
        if len(all_results) >= max_total:
            break
    return all_results

def construct_output(seoul_results: List[str], gyeonggi_results: List[str], matched_station_name: str, route_no: str, user_input_name: str) -> str:
    final_results = deduplicate_and_limit(seoul_results, gyeonggi_results, max_total=4)
    header = f"(입력: {user_input_name}) / 버스번호: {route_no}" # [정류장: {matched_station_name}] 입력값과 1차 매칭된 값. 혼란줄 것 같아 임의로 주석처리
    if final_results:
        return f"{header}\n" + "\n".join(final_results)
    else:
        return f"{header}\n도착 정보를 찾을 수 없습니다."

def get_bus_arrival(station_name: str, route_no: str) -> str:
    matched_station_name = find_best_stop_name(station_name, list(all_stop_names), threshold=0.4)
    seoul_results = get_seoul_arrival(route_no, matched_station_name)
    gyeonggi_results = get_gyeonggi_arrival_by_route_with_curl(route_no, matched_station_name)
    return construct_output(seoul_results, gyeonggi_results, matched_station_name, route_no, station_name)
