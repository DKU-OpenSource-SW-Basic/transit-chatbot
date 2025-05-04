import traffic

bus = traffic.BusInfo("역촌초등학교","753") 
traffic.ToolKit.enhancedPrintList(bus.getAPI("exps1"))
print(bus.findMatchingItemArray())

subway = traffic.SubwayInfo("서울","1호선","상행")
subway.getAPI()
print(subway.findMatchingItemArray())