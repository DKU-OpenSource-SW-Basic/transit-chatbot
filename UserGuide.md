# User Guide

## 다운로드 방법


- 원하는 폴더에 아래 명령어 입력하여 파일 다운로드
```bash
git clone https://github.com/DKU-OpenSource-SW-Basic/transit-chatbot.git
```
- setup_project.py 파일 실행
- http://127.0.0.1:8000/ 에 접속

## 실 사용 예
- 웹페이지의 기본 화면이다
- 아래 있는 공간에 채팅을 입력하여 대답을 받는다.

![웹 페이지 메뉴](.images/main_screen.png)

### 버스,지하철 도착 시간 구하기

- 지하철의 도착정보를 물어본 예시이다.

![지하철 도착시간 질문](.images/getSubwayInfo.png)
- 버스의 도착정보를 물어본 예시이다.

![버스 도착시간 질문](.images/getBusInfo.png)

### 즐겨찾기 사용방법
- 즐겨 찾기 기본 화면이다.
-  + 를 눌러서 새로운 즐겨찾기를 등록하거나
- 이전에 만든 것을 눌러서 채팅하지않고 도착정보를 바로 받을수 있다.

![즐겨찾기 메뉴](.images/favorite_menu.png)
- 이름을 지정하고 원하는 질문을 작성하여 저잘해둘수 있다.

![즐겨찾기 등록방법](.images/favorite_register.png)
- 블럭을 누르면 저장해둔 질문에 대한 도착정보를 알려준다.

![즐겨찾기 사용 방법](.images/favorite_use.png)