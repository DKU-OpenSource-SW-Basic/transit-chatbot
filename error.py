import requests

service_key = "1sq/rwVIQUlj/pGMERuN6nx+n6RE4Ioxf5ymfzg2LZgyne97Ex0Bmm4xBJ8jPFPHfFBhAOuXc///yNimFMb0jg=="
stationId = "217000373"
routeId = "216000007"
staOrder = "13"

url = f"https://apis.data.go.kr/6410000/busarrivalservice/v2/getBusArrivalItemv2?format=json&serviceKey={service_key}&staionId={stationId}&routeId={routeId}&staOrder={staOrder}"
response = requests.get(url)
