# subway_handler.py
import requests
from typing import Optional
from .intent_parser import get_first
from .subway_station_map import get_subway_statn_id, find_closest_station_name, get_exact_statn_id
import json
import os

# API 키
TAGO_API_KEY = "cLnyMQHDF8fbs1XyKC1w2N6zZKMFCEFsvyiGh5IQYuEyMeU8JQ3Hf8XNmPgYxBuWKLBYdQIkcKOHmobGMlEdDw%3D%3D"
SEOUL_API_KEY = "5a506c476b73696d39376845756c6a"

SEOUL_LINES = {"1호선", "2호선", "3호선", "4호선", "5호선", "6호선", "7호선", "8호선", "9호선", "경의중앙선", "수인분당선", "신분당선", "경춘선", "경강선", "우이신설선", "서해선", "신림선", "공항철도", "GTX-A"}

# Load subway station map once at the start
with open(os.path.join("Json", "Subway_Station.json"), "r", encoding="utf-8") as f:
    raw_data = json.load(f)

SUBWAY_MAP = {}
for entry in raw_data:
    line = entry["line_name"]
    station = entry["station_name"]
    station_id = entry["station_id"]

    if line not in SUBWAY_MAP:
        SUBWAY_MAP[line] = {}
    SUBWAY_MAP[line][station] = station_id


def get_subway_arrival(response_json: dict) -> str:

    # 1. 슬롯에서 리스트가 들어오는 것을 고려해 첫 번째 값만 추출
    station_list = response_json.get("response", {}).get("B-STATION", [])
    line_list = response_json.get("response", {}).get("B-LINE", [])

    station = station_list[0] if isinstance(station_list, list) and station_list else None
    line = line_list[0] if isinstance(line_list, list) and line_list else None

    if not station or not line:
        return "역 이름 또는 호선명이 누락되었습니다."

    # 2. 가장 유사한 역 이름 찾기
    station = find_closest_station_name(station, line)

    # 3. 역 ID 얻기
    statn_id = SUBWAY_MAP.get(line, {}).get(station)
    if not statn_id:
        return f"[{station} - {line}] 에 해당하는 지하철역 정보를 찾을 수 없습니다."

    result_lines = []

    if line in SEOUL_LINES:
        # 4. 서울시 API 사용
        try:
            url = (
                f"http://swopenapi.seoul.go.kr/api/subway/{SEOUL_API_KEY}/json/realtimeStationArrival/0/5/{station}"
            )
            res = requests.get(url)
            data = res.json()
            items = data.get("realtimeArrivalList", [])

            if not items:
                raise ValueError("서울시 응답이 비어 있음")
            
            result_lines.append(f"[{station}역 / {line} 도착 정보]\n")

            for item in items[:4]:
                dest = item.get("trainLineNm", "방면 미확인")
                msg = item.get("arvlMsg2", "도착 정보 없음")

                direction = dest.split(" - ")[0] if " - " in dest else dest

                # msg가 "전역 도착"이나 "과천 도착" 같은 경우 처리
                if "도착" in msg:
                    line_text = f"🔹 {direction} 방면 → 현재역 도착"
                else:
                    # 괄호가 있는 경우 역명만 추출
                    line_text = f"🔹 {direction} 방면 → {msg}"

                result_lines.append(line_text)


        except Exception as e:
            # 5. 실패 시 국토부 API 자동 전환
            try:
                url = (
                    f"https://apis.data.go.kr/1613000/SubwayInfoService/getSubwayArrivalInfo"
                    f"?serviceKey={TAGO_API_KEY}&statnId={statn_id}&_type=json"
                )
                res = requests.get(url)
                data = res.json()
                items = data["response"]["body"]["items"]["item"]

                result_lines.append(f"[{station} - {line} 도착 정보 (서울 실패 → 국토부 사용)]")
                if isinstance(items, list):
                    for item in items[:2]:
                        result_lines.append(f"• {item['trainNo']}열차: {item['arvlMsg2']}")
                else:
                    result_lines.append(f"• {items['trainNo']}열차: {items['arvlMsg2']}")
                return "\n".join(result_lines)
            except Exception as e2:
                return f"서울시/국토부 API 모두 실패: {e2}"

    else:
        # 6. 그 외 지역은 국토부 API 사용
        try:
            url = (
                f"https://apis.data.go.kr/1613000/SubwayInfoService/getSubwayArrivalInfo"
                f"?serviceKey={TAGO_API_KEY}&statnId={statn_id}&_type=json"
            )
            res = requests.get(url)
            data = res.json()
            items = data["response"]["body"]["items"]["item"]

            result_lines.append(f"[{station} - {line} 도착 정보 (국토부)]")
            if isinstance(items, list):
                for item in items[:2]:
                    result_lines.append(f"• {item['trainNo']}열차: {item['arvlMsg2']}")
            else:
                result_lines.append(f"• {items['trainNo']}열차: {items['arvlMsg2']}")
            return "\n".join(result_lines)
        except Exception as e:
            return f"국토부 API 실패: {e}"

    if result_lines:
        for line in result_lines:
            return "\n".join(result_lines)
    else:

        return "도착 정보 없음"



def get_subway_congestion(response_json: dict) -> str:
    station = get_first(response_json["response"].get("B-STATION"))
    line = get_first(response_json["response"].get("B-LINE"))

    if not station or not line:
        return "역 이름 또는 호선명이 누락되었습니다."

    station = find_closest_station_name(station, line)
    statn_id = SUBWAY_MAP.get(line, {}).get(station)
    if not statn_id:
        return f"[{station} - {line}] 에 해당하는 지하철역 정보를 찾을 수 없습니다."

    if line in SEOUL_LINES:
        return f"[{station} - {line}] 혼잡도 정보는 현재 제공되지 않는 API입니다. 양해 부탁드립니다."

    try:
        url = (
            f"https://apis.data.go.kr/1613000/SubwayInfoService/getSubwayCongestionInfo"
            f"?serviceKey={TAGO_API_KEY}&statnId={statn_id}&_type=json"
        )
        res = requests.get(url)
        data = res.json()
        items = data['response']['body']['items']['item']

        result_lines = [f"[{station} - {line} 혼잡도 정보 (국토부)]"]
        for item in items[:2]:
            time = item['timeSlot']
            level = item['congestionLevel']
            result_lines.append(f"• {time} 기준: 혼잡도 {level}단계")

        return "\n".join(result_lines)
    except Exception as e:
        return f"혼잡도 정보를 불러오지 못했습니다. ({e})"
