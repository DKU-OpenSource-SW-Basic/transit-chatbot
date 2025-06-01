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
    """전체 정류장 후보 중 가장 유사한 이름 반환 (없으면 입력값 반환)"""
    matches = difflib.get_close_matches(query, candidates, n=1, cutoff=threshold)
    return matches[0] if matches else query

def get_top_station_matches(query: str, top_n: int = 5) -> List[Tuple[str, dict, float]]:
    results = []
    for _, row in bus_stops.iterrows():
        name = row.get("정류소명")
        if pd.isna(name):
            continue
        score = similarity(query, str(name))
        results.append((name, row.to_dict(), score))

    exact_matches = [res for res in results if res[0].lower() == query.lower()]
    if exact_matches:
        return exact_matches

    sorted_results = sorted(results, key=lambda x: x[2], reverse=True)
    return sorted_results[:top_n]

def extract_possible_key(d: dict, candidates: List[str]) -> Optional[str]:
    lowered = {k.lower(): v for k, v in d.items() if pd.notna(v)}
    for key in candidates:
        if key.lower() in lowered:
            return str(lowered[key.lower()]).strip()
    return None

def clean_stop_id(value: Optional[str]) -> Optional[str]:
    try:
        return str(int(float(value)))
    except:
        return None

def get_seoul_arrival(route_no: str, station_name: str) -> Optional[str]:
    route_id = seoul_route_map.get(route_no)
    if not route_id:
        return None

    url = "http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRouteAll"
    params = {"serviceKey": SEOUL_SERVICE_KEY, "busRouteId": route_id}
    try:
        resp = requests.get(url, params=params, timeout=5)
        root = ET.fromstring(resp.content)
        items = root.findall(".//itemList")

        best_match = None
        best_score = 0
        for item in items:
            item_ars_id = item.findtext("arsId")
            item_node_id = item.findtext("stId")
            item_station_name = item.findtext("staNm")

            current_station_name = item_station_name
            if not current_station_name:
                local_matches = bus_stops[(bus_stops['NODE_ID'].astype(str) == str(item_node_id)) | (bus_stops['ARS_ID'].astype(str) == str(item_ars_id))]
                if not local_matches.empty:
                    current_station_name = local_matches.iloc[0].get("정류소명")

            if current_station_name:
                score = similarity(station_name, current_station_name)
                if score > best_score:
                    best_score = score
                    best_match = item

        if best_match and best_score > 0.7:
            remain_seat = best_match.findtext("reride_Num1")
            remain_text = "정보 없음" if remain_seat in ["-1", None] else remain_seat
            return f"[서울] {route_no} 버스: {best_match.findtext('arrmsg1')} / {best_match.findtext('arrmsg2')} / 이번 버스 잔여좌석: {remain_text}"

        return None
    except:
        return None

def get_gyeonggi_route_id(route_no: str) -> Optional[str]:
    matches = gyeonggi_routes[gyeonggi_routes["노선번호"] == route_no]
    return str(matches.iloc[0]["노선ID"]) if not matches.empty else None

def get_gyeonggi_arrival_by_route_with_curl(route_no: str, station_name: str) -> List[str]:
    route_id = get_gyeonggi_route_id(route_no)
    if not route_id:
        return []

    list_url = f"https://apis.data.go.kr/6410000/busrouteservice/v2/getBusRouteStationListv2?serviceKey={GYEONGGI_SERVICE_KEY}&routeId={route_id}&format=json"
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

        matching_stations = []
        min_similarity_threshold = 0.4
        for station in station_list:
            current_station_name = station.get("stationName")
            if current_station_name:
                score = similarity(station_name, current_station_name)
                if score >= min_similarity_threshold:
                    matching_stations.append(station)

        gyeonggi_arrival_results = []
        processed_stop_ids = set()

        for station in matching_stations:
            stop_id = station.get("stationId")
            if stop_id and stop_id not in processed_stop_ids:
                processed_stop_ids.add(stop_id)

                arrival_url = f"https://apis.data.go.kr/6410000/busarrivalservice/v2/getBusArrivalItemv2?serviceKey={GYEONGGI_SERVICE_KEY}&stationId={stop_id}&routeId={route_id}&format=json"
                command_arrival = shlex.split(f"curl -k '{arrival_url}'")
                process_arrival = subprocess.Popen(command_arrival, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout_arrival, _ = process_arrival.communicate()

                if process_arrival.returncode != 0:
                    continue

                try:
                    data_arrival = json.loads(stdout_arrival)
                    arrival_item = data_arrival.get("response", {}).get("msgBody", {}).get("busArrivalItem")

                    if arrival_item:
                        predict_time = arrival_item.get('predictTime1')
                        remain_seat = arrival_item.get('remainSeatCnt1')
                        remain_text = "정보 없음" if remain_seat is None or remain_seat == -1 else str(remain_seat)
                        if predict_time is not None and str(predict_time).isdigit():
                            gyeonggi_arrival_results.append(f"[경기] {route_no} 버스: {predict_time}분 / 이번 버스 잔여좌석: {remain_text}")
                except json.JSONDecodeError:
                    continue

        return gyeonggi_arrival_results
    except:
        return []

def construct_output(seoul_results: List[str], gyeonggi_results: List[str], matched_station_name: str, route_no: str, user_input_name: str) -> str:
    seen = set()
    unique = []
    for entry in seoul_results + gyeonggi_results:
        if entry not in seen:
            seen.add(entry)
            unique.append(entry)
    header = f"[정류장: {matched_station_name}] (입력: {user_input_name}) / 버스번호: {route_no}"
    if unique:
        return f"{header}\n" + "\n".join(unique)
    else:
        return f"{header}\n도착 정보를 찾을 수 없습니다."

def get_bus_arrival(station_name: str, route_no: str) -> str:
    # 유사도 기반으로 최적의 정류장명 추출 (서울/경기 전체 DB 대상)
    matched_station_name = find_best_stop_name(station_name, list(all_stop_names), threshold=0.4)

    seoul_results = []
    seoul_result = get_seoul_arrival(route_no, matched_station_name)
    if seoul_result:
        seoul_results.append(seoul_result)

    gyeonggi_results = get_gyeonggi_arrival_by_route_with_curl(route_no, matched_station_name)

    return construct_output(seoul_results, gyeonggi_results, matched_station_name, route_no, station_name)

