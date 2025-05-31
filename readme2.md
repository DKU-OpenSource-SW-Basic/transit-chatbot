# User Guide
## 목표 사용자
- 자신이 기다리는 대중교통이 언제 오는지 알고 싶은 사용자
## 사용 목적
- 서울,경기 지역의 지하철과 버스 도착정보를 제공하는것이다.
- 웹 사이트에서 텍스트 기반 챗봇과 상호작용하여 도착정보를 받아온다.
## 사용 시나리오

## 실제 사용 화면


#### 버스 도착시간 요청
- 사이트의 채팅 화면에서 챗봇 실행
- 질문에 정류장 이름과 버스 번호를 포함하여 질문한다.
- 잠시후 챗봇이 질문한 정류장에 도착하는 가장빠른 질문한 버스가 두개의 예상 도착정보를 제공한다.
#### 지하철 도착시간 요청
- 사이트의 채팅 화면에서 챗봇 실행
- 질문에 역 이름과 지하철 호선 정보를 포함하여 질문한다.
- 잠시후 챗봇이 질문한 역에 가장빠른 질문한 지하철 두개의 예상 도착정보를 알려준다.

# Developer Guide
## 사전준비
- Python 3.8 이상 필요
- git
- 공공 데이터 포털의 APIKey **사용API보고 https://www.data.go.kr/ 에서 신청필요**
## 다운로드 방법
``` bash
git clone https://github.com/DKU-OpenSource-SW-Basic/transit-chatbot.git
```
``` terminal
python manage.py runserver
```

##  📁 파일 구조
``` 
├── Json/                   # 버스,지하철 ID 정보 디렉토리 
├── chatbot/                # Django 폴더
├── chatbot_project/        # Django 폴더
├── traffic.py              # 도착정보 API 정리 클래스 
├── main.py                 # 도착정보 실행 예제
├── manage.py               
├── db.sqlite3              
├── download_model.py       
├── run_Koelectra.py        
└── README.md               # 유저 가이드 + 개발자 가이드
``` 
## 다이어 그램




# 사용 API
- **경기도버스 API** : https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15080346
- **서울버스 API** :https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15000314
- **지하철 API**: https://data.seoul.go.kr/dataList/OA-12601/A/1/datasetView.do;jsessionid=D01BCC4A262086FBB94C62C74D1A81DA.new_portal-svr-21
# 사용한 라이브러리
- requests
- urllib.parse
- xml.etree.ElementTree as ET
- json