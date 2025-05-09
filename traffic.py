import requests
import xml.etree.ElementTree as ET
import json
import urllib.parse

class ToolKit:
    @staticmethod
    def enhancedPrintList(list):
        for i,item in enumerate(list,1):
            print(f"{i}.{item}")
    @staticmethod
    def isNone(target):
        if target == None:
            return True
        return False
    @staticmethod
    def readJson(filePath)->list :
        with open(filePath,"r",encoding="utf-8") as f:
            data = json.load(f)
        bus_list = data["DATA"]
        return bus_list
# class BusInfo:
#     bus_number = None
#     bus_list=None
#     route_id=None
#     bus_stop_name= None
#     root = None
#     bus_dict = []
#     service_key = "1sq/rwVIQUlj/pGMERuN6nx+n6RE4Ioxf5ymfzg2LZgyne97Ex0Bmm4xBJ8jPFPHfFBhAOuXc///yNimFMb0jg=="
#     def __init__(self,bus_stop_name:str,bus_num:str):
#         self.bus_number = bus_num
#         self.bus_stop_name = bus_stop_name
#         self.bus_list = ToolKit.readJson("Json/busRouteId.json")
#         self.getRouteIdByBusNumber()
#     def findMatchingItemArray(self):
#         returnArray = []
#         for item in self.bus_dict:
#             if(item[0]==self.bus_stop_name):
#                 for time in item[1:]:
#                     returnArray.append(time)
#         return returnArray
#     def getMatchingItems(self,items,tag:str):
#         if(items.tag==tag):
#             return items.text
#         else : 
#             return None
#     def getRouteIdByBusNumber(self):
#         for bus in self.bus_list:
#             if bus["transport_name"] == self.bus_number:
#                 self.route_id = bus["transport_id"]
#                 return
#             else:
#                 self.route_id = None
#     def getAPI(self,value_tag:str):
#         url = 'http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRouteAll'
#         params ={'serviceKey' : self.service_key, 'busRouteId' : self.route_id }
#         response = requests.get(url, params=params)
#         self.root = ET.fromstring(response.content)
#         stNm_dict = []
#         value_dict = []
#         print(self.root.findall(".//itemList"))
#         for item in self.root.findall(".//itemList"):
#             for child in item:
#                 stNm = self.getMatchingItems(child,"stNm")
#                 if not ToolKit.isNone(stNm): stNm_dict.append(stNm)
#                 value = self.getMatchingItems(child,value_tag)
#                 if not ToolKit.isNone(value): value_dict.append(value)
#         if len(stNm_dict)==len(value_dict):
#             self.bus_dict = list(zip(stNm_dict,value_dict))
#         else:
#             self.getAPI("stNm",value_tag)
#         return self.bus_dict
# class SubwayInfo:
#     service_key = "5a506c476b73696d39376845756c6a"
    
#     data = None
#     station_name = None
#     subway_dict = []
#     subway_list = None
#     subway_id = None
#     subway_name = None
#     updn_line = None
#     def __init__(self,station_name,subway_num,updn_line):
#         self.station_name=station_name
#         self.subway_name = subway_num
#         self.updn_line = updn_line
#         self.subway_list = ToolKit.readJson("Json/subwayId.json")
#         self.convertSubwayNameToId()
#     def convertSubwayNameToId(self):
#         for subway in self.subway_list:
#             if subway["transport_name"] == self.subway_name:
#                 self.subway_id = subway["transport_id"]
#                 # print(self.subway_id)
#                 return
#             else:
#                 self.route_id = None
#     def getAPI(self):
#         url = 'http://swopenapi.seoul.go.kr/api/subway/{}/json/realtimeStationArrival/0/20/{}'.format(
#             urllib.parse.quote(self.service_key),
#             urllib.parse.quote(self.station_name)  # 조회할 역 이름
#         )
#         response = requests.get(url)
#         self.data = response.json()
#     def findMatchingItemArray(self):
#         returnArray =[]
#         for item in self.data['realtimeArrivalList']:
#             if item['subwayId'] == self.subway_id and item['updnLine'] == self.updn_line:
#                 returnArray.append(item['barvlDt'])
#         return returnArray
class TransportInfo:
    direction = None
    station_name = None
    transport_num = None
    transport_id = None
    transport_id_list = None
    transport_dict = []
    def updateInfo(self,station_name,transport_num,direction):
        self.direction=direction
        self.station_name = station_name
        self.transport_num = transport_num
        self.convertTransportNameToId()
        # direction,station,trNum,trId 입력완료
    def getArrivalInfo(self):
        pass
    def convertTransportNameToId(self):
        for transport in self.transport_id_list:
            if transport["transport_name"] == self.transport_num:
                self.transport_id = transport["transport_id"]
                return
            else:
                self.transport_id = None
    def checkInputException(self):
            if self.direction:
                return "direction is undefineded/check updateInfo"
            if self.direction not in ('상행','하행'):
                return "direction does not match the condition/check updateInfo"
            if not self.transport_num : 
                return "transport_num is undefineded/check updateInfo"
            if not self.station_name : 
                return "station_name is undefineded/check updateInfo"
            if not self.transport_id_list:
                return "transport_id_list is undefineded/check constructor"
class BusInfo(TransportInfo):
    def __init__(self):
        self.transport_id_list = ToolKit.readJson("Json/busRouteId.json")
    def getArrivalInfo(self):
        url = 'http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRouteAll'
        params ={'serviceKey' : "1sq/rwVIQUlj/pGMERuN6nx+n6RE4Ioxf5ymfzg2LZgyne97Ex0Bmm4xBJ8jPFPHfFBhAOuXc///yNimFMb0jg==", 'busRouteId' : self.transport_id}
        response = requests.get(url, params=params)
        root = ET.fromstring(response.content)
        for item in root.iter("itemList"):
            immi_dict = {child.tag: child.text for child in item}
            self.transport_dict.append(immi_dict)
        returnArray=[]
        for item in self.transport_dict:
            if item['stNm'] == self.station_name:
                returnArray.append((item['arrmsg1'],item['arrmsg2']))
        if self.direction == "상행":
            return returnArray[0]
        return returnArray[1]
    
class SubwayInfo(TransportInfo):
    def __init__(self):
        self.transport_id_list = ToolKit.readJson("Json/subwayId.json")
    def getArrivalInfo(self):
        self.checkInputException()
        url = 'http://swopenapi.seoul.go.kr/api/subway/{}/json/realtimeStationArrival/0/20/{}'.format(
            urllib.parse.quote("5a506c476b73696d39376845756c6a"),
            urllib.parse.quote(self.station_name)  
        )
        response = requests.get(url)
        data = response.json()
        
        if data['errorMessage'].get('code') != 'INFO-000':
            return data['errorMessage'].get('message')
        for item in data['realtimeArrivalList']:
            # print(f"{item['subwayId']}:{self.transport_id}/{item['updnLine']}")
            if item['subwayId'] == self.transport_id and self.isSameDirection(self.direction,item['updnLine']):
                # print(f"{item['arvlMsg2']}/{item['subwayId']}/{item['barvlDt']}")
                return item['arvlMsg2']
        return 'item not founded'
    def isSameDirection(self,dirct1,dirct2):
        UPWARD =('상행','내선')
        DOWNWARD=('하행','외선')
        if dirct1 in UPWARD:
            return dirct2 in UPWARD
        return dirct2 in DOWNWARD