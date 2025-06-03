# 🚀 User Guide

## 🛠️ 다운로드 방법

**방법 1**
``` bash
# 1. 깃허브에서 프로젝트를 복제(clone)합니다.
git clone https://github.com/DKU-OpenSource-SW-Basic/transit-chatbot.git

# 2. 생성된 프로젝트 폴더로 이동합니다.
cd transit-chatbot

# 3. (최초 1회) 모든 환경 준비 및 실행을 자동으로 처리합니다.
python setup_project.py
```
``` terminal
python manage.py runserver
```
``` bash
만약 python manage.py runserver 명령어로 실행했는데 404가 뜬다면,
where manage.py
코드를 실행하여 경로를 확인하고, transit-chatbot 폴더가 아닌 경로로 지정되어 있거나 비어있다면
python manage.py runserver --settings=chatbot_project.settings
명령어를 입력하시면 해결될 수 있습니다.
```

**방법 2**

>1. `Download ZIP`을 활용하여 직접 전체 코드를 다운로드합니다.
>2. 원하는 경로에 압축을 풀고, `setup_project.py`을 실행합니다.
>3. 만약, 제대로 웹페이지가 나오지 않는다면, `setup_project.py`를 강제종료 혹은 직접 종료하고 다시 실행하고 기다립니다.
>4. 열려있는 py창을 닫을경우 강제로 웹페이지와의 연결이 끊깁니다. 


## 📖 사용 방법
- 웹페이지의 기본 화면이다
- 아래 있는 공간에 채팅을 입력하여 대답을 받는다.  
![웹 페이지 메뉴](images/recropped_1.png)

### 🧩 버스,지하철 도착 시간 구하기

- 지하철의 도착정보 및 혼잡도를 물어본 예시이다. 현재 API문제로 혼잡도 질문은 지원하지 않는다.   
![지하철 도착시간 질문](images/recropped_3.png) <br>
- 각각 경기 버스와 서울 버스의 도착정보를 물어본 예시이다.  
![버스 도착시간 질문](images/recropped_2.png)

### 🧩 즐겨찾기 사용방법
- 즐겨찾기 기본 화면이다. 우측 상단의 `★즐겨찾기` 버튼을 눌러 활성화할 수 있다. 
- `+`를 눌러서 새로운 즐겨찾기를 등록할 수도 있고, 기존에 등록해두었던 즐겨찾기를 통해 바로 질문을 할 수도 있다. 
![즐겨찾기 기본화면](images/recropped_4.png) <br>
- 기존에 등록해둔 즐겨찾기를 누르면 저장해 둔 문장으로 바로 질문을 한다.
- `과천청사 2번출구 역에서 7007-1번 버스가 언제쯤 도착하는지 알려주시겠습니까?`라는 문장이 즉시 입력되며, 바로 결과를 보여주는 것을 알 수 있다. 
![즐겨찾기 기본화면](images/recropped_5.png) <br>
- 즐겨찾기 이름을 지정할 수 있고, 그 문장을 저장할 수 있다. 
![즐겨찾기 메뉴](images/recropped_6.png) <br>
- 방금 입력했던 문장이 즐겨찾기 이름으로 저장되는 것을 확인할 수 있다. 
- 저장된 즐겨찾기 버튼을 누르면, 방금 저장했던 그 문장을 즉시 사용하는 것을 볼 수 있다. 
![즐겨찾기 등록방법](images/recropped_7.png)

### 🧩 지원하지 않는 질문, 부족한 정보에 대한 질문 처리
- 역/정거장의 정보를 누락했거나, 버스/지하철의 대한 정보를 입력하지 않았을 경우 사용자에게 정보를 제공하지 않는다. 
![부족한 정보](images/recropped_last.png) <br>
- 역/정거장의 정보를 잘못 입력했거나, 아직 배차가 되지 않거나 하는 등의 이유로 정보를 제대로 받지 못했을 경우 아래와 같은 문구가 나온다.
- `의정부경전철`, `용인경전철`, `인천1,2호선`같은 경우는 해당 API에서 지원하지 않아 아직은 정보를 얻을 수 없다.
![잘못된 정보](images/recropped_final.png)
