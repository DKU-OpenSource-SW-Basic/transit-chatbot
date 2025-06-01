from .bus_handler import get_bus_arrival
from .subway_handler import get_subway_arrival, get_subway_congestion
import requests

def dispatch(intent, keywords):
    def get_first(lst):
        return lst[0] if lst and len(lst) > 0 else None

    try:
        if intent == "arrival_bus":
            station = get_first(keywords.get("B-STATION"))
            route = get_first(keywords.get("B-ROUTE"))
            if not station:
                return "정류장명을 입력해주세요."
            if not route:
                return "버스 번호를 입력해주세요."
            result = get_bus_arrival(station, route)
            if not result or "도착 정보를 찾을 수 없습니다." in result:
                return f"{station} 정류장의 {route}번 버스 실시간 정보를 찾을 수 없습니다. (운행 시간 외이거나, 등록된 정보가 없습니다.)"
            return result

        elif intent == "arrival_subway":
            station = get_first(keywords.get("B-STATION"))
            line = get_first(keywords.get("B-LINE"))
            if not station:
                return "지하철역 이름을 입력해주세요."
            if not line:
                return "몇 호선인지 입력해주세요."
            result = get_subway_arrival({"response": keywords})
            if not result or "정보를 찾을 수 없습니다" in result:
                return f"{station}역 {line}호선의 실시간 도착 정보를 찾을 수 없습니다. (운행 시간 외이거나, 등록된 정보가 없습니다.)"
            return result

        elif intent == "congestion":
            # 현재 혼잡도 API는 종료 상태이므로 별도 안내
            return "지하철 혼잡도 정보는 현재 제공하지 않습니다. 다른 문의를 입력해 주세요."

        elif intent == "other":
            return "정확한 질문을 입력해 주세요. 예: '강남역 2호선 도착 시간 알려줘' 처럼 입력해 주시면 됩니다."

        else:
            return f"[{intent}] {keywords}"

    except requests.exceptions.SSLError:
        return "서버의 인증서 문제로 정보를 받아올 수 없습니다. 잠시 후 다시 시도해 주세요."
    except requests.exceptions.ConnectionError:
        return "서버와의 연결에 실패했습니다. 인터넷 연결이나 서버 상태를 확인해 주세요."
    except requests.exceptions.Timeout:
        return "서버 요청이 시간 내에 완료되지 않았습니다. 잠시 후 다시 시도해 주세요."
    except Exception as e:
        err_msg = str(e)
        if "인증" in err_msg or "apikey" in err_msg:
            return "API 인증 오류가 발생했습니다. 관리자에게 문의해 주세요."
        return f"시스템 오류가 발생했습니다. 관리자에게 문의해 주세요.\n{err_msg}"
