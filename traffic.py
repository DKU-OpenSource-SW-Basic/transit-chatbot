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
    def readJson(filePath)->list :
        with open(filePath,"r",encoding="utf-8") as f:
            data = json.load(f)
        bus_list = data["DATA"]
        return bus_list
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
            return returnArray[0]
    
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
            if item['subwayId'] == self.transport_id :
                return item['arvlMsg2']
        return 'item not founded'
