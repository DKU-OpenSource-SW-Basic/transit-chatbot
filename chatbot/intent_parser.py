def get_first(lst):
    return lst[0] if lst and isinstance(lst, list) and len(lst) > 0 else None

def parse_intent_to_api_params(model_output):
    """
    모델 출력값에서 실제 API 호출에 필요한 파라미터를 추출합니다.
    예:
    {
        "intent": "arrival_bus",
        "B-STATION": ["과천정부청사"],
        "B-ROUTE": ["101"],
        "B-LINE": []
    }
    → {"station": "과천정부청사", "route": "101", "line": None}
    """
    return {
        "station": get_first(model_output.get("B-STATION")),
        "route": get_first(model_output.get("B-ROUTE")),
        "line": get_first(model_output.get("B-LINE"))
    }