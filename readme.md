## 📘 프로젝트 소개
서울시에서 제공하는 버스및 지하철 도착정보를 OpenAI를 활용해서 도착예정 시간을 조회하는 Python 프로그램
## 사용한 라이브러리
- requests
- urllib.parse
- xml.etree.ElementTree as ET
- json
##  📁 파일 구조
``` 
├── traffic.py              # BusInfo, SubwayInfo 클래스 정의 
├── main.py                 # 실행 예제 
├── Json/                   # json 파일 디렉토리 
│ ├── busRouteId.json       # 버스 노선 데이터 
│ └── subwayId.json         # 지하철 노선 데이터 
└── README.md 
``` 

            
## 📦 클래스 및 메소드 설명

### 🧩 Class : ToolKit

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

### 🧩 Class : TransportInfo
**BusInfo 와 SubwayInfo의 부모 클래스이다.** 

#### 🔸 `updateInfo(station_name,transport_num,direction)`
```python
transport = TransportInfo()
transport.updateInfo(name,num,"상행")
```
**기능** : 역이름,대중교통의 번호,상행/하행 인지를 입력받는다.

첫 객체 생성후 반드시 사용해야하며 후에 바꾸고 싶을떄 다시 입력하여 값을 바꿀수있다다

#### 🔸 `checkInputException()`
**기능** : updateInfo로 받은 값들이 조건에 맞는지 확인한다

#### 🔸 `convertTransportNameToId()`
**기능** : 대중교통의 이름(ex:1호선,753) 을 ID값으로 변환후 transport_id 에 저장한다

#### 🔸 `getArrivalInfo()`
**기능** : 대중교통이 언제 도착하는지 정보를 반환한다. 세부내용은 자식클래스에서 개발한다.
```python
print(transport.getArrivalInfo())
```

### 🧩 Class : BusInfo
 

#### 🛠 생성자
**기능** busID에 관한 json파일을 읽어 값을 dict로 저장한다.
```python
bus = BusInfo()
```

#### 🔸 `getArrivalInfo()`
**기능** 버스가 언제 도착할지를 반환한다.
- 내부에 출력할값을 arrmsg1과arrmsg2로 설정해두었는데 이는 첫번쨰와두번쨰 도착할 버스의 도착정보를 받기 위함이고 다른걸 받으려면 아래있는 사이트에 있는 파라미터를 골라서 바꾸면 된다.
- 또한 정보를 받아올떄 노선 전체를 받아오기에 종점방향으로 향하는 상행버스와 하행버스를 구별할수있게 두개를 전부 구하고 하나만 취하는것으로 만들었다. 

### 🧩 Class : SubwayInfo

#### 🛠 생성자
**기능** subwayID에 관한 json파일을 읽어 값을 dict로 저장한다
```python
subway =SubwayInfo()
```

#### 🔸 `getArrivalInfo()`
**기능** 지하철이 언제 도착할지를 반환한다.
- 만약 대답이 error로 오게 된다면 errorMessage가 출력된다.
- 도착정보를 받기위해 arvlMsg2로 설정했는데 다른 정보를 출력하고싶다면 아래있는 사이트에서 파라미터를 골라서 바꾸면 된다.

#### 🔸 `isSameDirection(dirct1,dirct2)`
**기능** 지하철의 경우 내선과 외선이 있기에 dirct1이 상행일떄 dirct2가 상행이거나 내선이어도 참을 반환하고 dirct1이 하행일떄 dirct2가 하행이거나 외선일떄 참을 반환한다.

## 참고
**버스 API** :https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15000314

**지하철 API**: https://data.seoul.go.kr/dataList/OA-12601/A/1/datasetView.do;jsessionid=D01BCC4A262086FBB94C62C74D1A81DA.new_portal-svr-21

## 미구현 기능들
- ❌ 즐겨찾기 
- ❌ 지하철 혼잡도
- 