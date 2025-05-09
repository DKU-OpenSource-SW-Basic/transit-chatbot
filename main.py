import traffic 
from traffic import ToolKit

# bus = traffic.BusInfo("역촌초등학교","753") 
# bus.getAPI("exps1")

bus = traffic.BusInfo()
bus.updateInfo("역촌초등학교","753","하행")
print(bus.getArrivalInfo())


sub = traffic.SubwayInfo()
sub.updateInfo("강남",'2호선','상행')
print(sub.getArrivalInfo())
