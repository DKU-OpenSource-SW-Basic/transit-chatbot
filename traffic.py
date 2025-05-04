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
class BusInfo:
    bus_number = None
    bus_list=None
    route_id=None
    bus_stop_name= None
    root = None
    bus_dict = []
    service_key = "service_key"


    def __init__(self,bus_stop_name:str,bus_num:str):
        self.bus_number = bus_num
        self.bus_stop_name = bus_stop_name
        self.bus_list = ToolKit.readJson("Json/busRouteId.json")
        self.getRouteIdByBusNumber()
    def findMatchingItemArray(self):
        returnArray = []
        for item in self.bus_dict:
            if(item[0]==self.bus_stop_name):
                for time in item[1:]:
                    returnArray.append(time)
        return returnArray
    def getMatchingItems(self,items,tag:str):
        if(items.tag==tag):
            return items.text
        else : 
            return None
    def getRouteIdByBusNumber(self):
        for bus in self.bus_list:
            if bus["route_name"] == self.bus_number:
                self.route_id = bus["route_id"]
                return
            else:
                self.route_id = None
    def getAPI(self,value_tag:str):
        url = 'http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRouteAll'
        params ={'serviceKey' : self.service_key, 'busRouteId' : self.route_id }
        response = requests.get(url, params=params)
        self.root = ET.fromstring(response.content)
        stNm_dict = []
        value_dict = []
        for item in self.root.findall(".//itemList"):
            for child in item:
                stNm = self.getMatchingItems(child,"stNm")
                if not ToolKit.isNone(stNm): stNm_dict.append(stNm)
                value = self.getMatchingItems(child,value_tag)
                if not ToolKit.isNone(value): value_dict.append(value)
        if len(stNm_dict)==len(value_dict):
            self.bus_dict = list(zip(stNm_dict,value_dict))
        else:
            self.getAPI("stNm",value_tag)
        return self.bus_dict
class SubwayInfo:
    service_key = "service_key"
    
    data = None
    station_name = None
    subway_dict = []
    subway_list = None
    subway_id = None
    subway_name = None
    updn_line = None
    def __init__(self,station_name,subway_num,updn_line):
        self.station_name=station_name
        self.subway_name = subway_num
        self.updn_line = updn_line
        self.subway_list = ToolKit.readJson("Json/subwayId.json")
        self.convertSubwayNameToId()
    def convertSubwayNameToId(self):
        for subway in self.subway_list:
            if subway["subway_name"] == self.subway_name:
                self.subway_id = subway["subway_id"]
                # print(self.subway_id)
                return
            else:
                self.route_id = None
    def getAPI(self):
        url = 'http://swopenapi.seoul.go.kr/api/subway/{}/json/realtimeStationArrival/0/20/{}'.format(
            urllib.parse.quote(self.service_key),
            urllib.parse.quote(self.station_name)  # 조회할 역 이름
        )
        response = requests.get(url)
        self.data = response.json()
    def findMatchingItemArray(self):
        returnArray =[]
        for item in self.data['realtimeArrivalList']:
            if item['subwayId'] == self.subway_id and item['updnLine'] == self.updn_line:
                returnArray.append(item['barvlDt'])
        return returnArray

