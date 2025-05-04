## 📘 프로젝트 소개
서울시에서 제공하는 버스및 지하철 도착정보를 OpenAI를 활용해서 도착예정 시간을 조회하는 Python 프로그램
## 사용한 라이브러리
- requests
- urllib.parse
- xml.etree.ElementTree as ET
- json
## 파일 구조
├── traffic.py               # BusInfo, SubwayInfo 클래스 정의
├── main.py                  # 실행 예제
├── Json/                    # json 파일 디렉토리
│   ├── busRouteId.json      # 버스 노선 데이터
│   └── subwayId.json        # 지하철 노선 데이터
└── README.md               
## 📦 클래스 및 메소드 설명

### Class : ToolKit

**기능**: 유틸리티 함수 모음 클래스 (출력, JSON 파일 읽기)

#### 🔸 enhancedPrintList(list : list)
- 리스트의 각 요소를 번호와 함께 출력합니다.
- **Parameter**
    - list (list) : 출력할 list
- **Returns** : None

#### 🔸 readJson(filepath :str) -> list
-  JSON 파일을 읽고 ["DATA"] 필드 안의 리스트를 반환합니다.
- **Parameter**
    - filepath (str) : JSON 파일 경로
- **Returns** : list

---

### Class : BusInfo
'BusInfo' 클래스는 버스 번호("bus_num")과 정류장 이름('bus_stop_name')을 기반으로 서울시 버스 실시간 정보를 조회 합니다.

#### 🛠 생성자
--python
BusInfo(bus_stop_name:str,bus_num:str)



#### 🔸 `getRouteIdByBusNumber()-> None`
**기능**
JSON에서 해당버스 번호(`bus_number`)에 해당하는 `route_id` 값을 찾아서 필드 변수에 저장합니다.

**Returns**: `None`

#### 🔸 `getAPI(value_tag)->list`

**기능**
서울특별시 버스도착정보조회 서비스 `getArroyInfoByRouteAllList` OpenAPI를 호출하여 매개변수에 작성한 태그에 맞는 값과 정류장 이름을 `bus_dict`에 저장하고 `bus_dict`값을 반환한다.

##### Parameters
- **value_tag** : 알고 싶은 tag값 
*tag*
- arsId : 정류장 번호
- busRouteId : 노선ID
- exps1 : 첫번쨰 도착 버스의 지수평활 도착예정 시간
- exps2 : 첫번쨰 도착 버스의 지수평활 도착예정 시간
- rtNm : 노선명
- https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15000314 추가 태그들들

#### 🔸 `findMatchingItemArray()`

**기능**
`bus_dict`에서 `bus_stop_name`이 같은 것의 `value`값을 배열 형식으로 반환한다.

### Class : SubwayInfo

#### 생성자
--Python
subway =SubwayInfo(역이름,호선명,상행여부)

#### `getAPI()`
**기능** 
생성자에서 받은 `staion_name`으로 서울시 지하철 실시간 열차 위치정보 API를 요청하여 얻은 값을 data에 저장한다.

#### `findMatchingItemArray()`

**기능** 
`data`에서 `subwayId` 와 상행여부가 필드값과 같은지 확인하고 같으면 이떄 도착 예정시간을 배열에 추가한후에 이를 반환한다.

## 참고
**버스 API**
https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15000314
**지하철 API**
https://data.seoul.go.kr/dataList/OA-12601/A/1/datasetView.do;jsessionid=D01BCC4A262086FBB94C62C74D1A81DA.new_portal-svr-21










