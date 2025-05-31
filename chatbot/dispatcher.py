from intent_parser import parse_intent_to_api_params
from transport_api import get_bus_arrival, get_subway_arrival, get_subway_congestion


def dispatch_request(model_output):
    intent = model_output.get("intent")
    parsed = parse_intent_to_api_params(model_output)

    if intent == "arrival_bus":
        return get_bus_arrival(parsed["station"], parsed["route"])

    elif intent == "arrival_subway":
        return get_subway_arrival(parsed["station"], parsed["line"])

    elif intent == "congestion":
        return get_subway_congestion(parsed["station"], parsed["line"])

    return "지원하지 않는 요청입니다."