import json
import heapq as hq
import math
from geopy.geocoders import Nominatim

def importFiles(edgepath, nodepath):
    with open(nodepath) as f: #data/walknodes.geojson
        nodes = json.load(f)

    with open(edgepath) as f: #data/walkedges.geojson
        edges = json.load(f)
    
    #return as dicts/list
    return nodes, edges
    
def convertToCoord(path, nodes):
    route = []
    for id in path:
        route.append([nodes[id][0]['lat'],nodes[id][0]['lon']])
    
    return route
    #return a list of coordinates to plot

def findNearestLrt(lrtstation, x, y):
    heulist = []
    for key, value in lrtstation.items():
        hval = heuristic(x, y, value[1], value[0])
        heulist.append((hval,key,value[1],value[0],value[2]))
    hq.heapify(heulist)
    dist1,key1,x1,y1, name1 = hq.heappop(heulist)
    return dist1, key1, x1, y1, name1
    
    
def findNearestBusStop(busstops, x, y):
    heulist = []
    for key, value in busstops.items():
        hval = heuristic(x,y,value['lat'],value['lon'])
        heulist.append((hval,key,value['name'], value['lat'],value['lon']))
    hq.heapify(heulist)
    heuris, bsCode, bsName, lat, lon = hq.heappop(heulist)
    print(heuris, bsName)
    return bsCode, bsName, lat, lon

#A* algorithm (priority)f(s) = (cost)g(s) + h(s)(estimation of remaining cost - heuristic)
def heuristic(x1,y1,x2,y2):
    #euclidean distance heuristic but omit square root to improve performance.
    #non-admissible as distance could be more than the heuristic of original start to end
    #return math.sqrt(math.pow((x1 - x2),2) + math.pow((y1 - y2),2))
    lon1, lat1, lon2, lat2 = map(math.radians,[y1, x1, y2, x2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def convertToAddress(start,end,route, nodesdict):
    start = str(start[0]) + "," + str(start[1])
    geolocation = Nominatim(user_agent="agent")
    location = geolocation.reverse(start,timeout=30)
    address = location[0] + "\n"
    prev = location[0]
    for id in route:
        if nodesdict[id][0]['ref'] != prev:
            address += nodesdict[id][0]['ref'] + "\n"
            prev = nodesdict[id][0]['ref']
    end = str(end[0]) + "," + str(end[1])
    location = geolocation.reverse(end,timeout=30)
    if location[0] != prev:
        address += location[0] + "\n"
    return address

#dijkstra for walk/drive/lrt
def dijkstra(start, end, edgesdict, nodesdict):
    heap = [(0,start,[])] #cost, current node, path
    hq.heapify(heap) #heapify the list (Just to make sure)
    visited = [] #visited nodes
    dist = {start:0} #initialize all other nodes distance to infinity
    while True:
        total_dist, cur_vertex, cur_path = hq.heappop(heap)
        #check if current vertex has been visited
        if cur_vertex in visited or cur_vertex not in edgesdict:
            continue
        #else append into visited list
        visited.append(cur_vertex)
        new_path = cur_path + [cur_vertex]
        #return condition
        if(cur_vertex == end):
            return cur_path, total_dist
        for node, cur_dist in edgesdict[cur_vertex]:
            if node not in dist or total_dist + cur_dist < dist[node]:
                dist[node] = cur_dist + total_dist
                priority = cur_dist + total_dist + heuristic(nodesdict[node][0]['lat'],nodesdict[node][0]['lon'],nodesdict[end][0]['lat'],nodesdict[node][0]['lon'])
                hq.heappush(heap,(priority, node, new_path))
        
        
#dijkstra for buses, cost of transfer determines distance traveled and number of transfers
def dijkstra_for_bus(start, end, edgesdict,cost_per_transfer):
    heap = [(0, 0, 0, [(start, None)])] #cost, current node, path curr_cost, curr_distance, curr_transfers, path
    hq.heapify(heap) #heapify the list (Just to make sure)
    visited = [] #visited nodes
    dist = {(start,None):0} #initialize all other nodes distance to infinity
    while True:
        #cost including cost for transfer, distance aka means bus distance in metre, curr_transfers hold the value of how
        #many bus taken.
        #path include the node visited and the service taken.
        curr_cost, total_dist, curr_transfers, path = hq.heappop(heap)
        # get the last node from the path
        (node, curr_service) = path[-1]
        

        #check if current vertex has been visited
        if (node, curr_service) in visited or node not in edgesdict:
            continue
            
        #else append into visited list
        visited.append((node, curr_service))
        #return condition
        if node == end:
            return total_dist, curr_transfers, path

        
        for adj_node, cur_dist, bus, service in edgesdict[node]:
            if (adj_node,service) not in dist or curr_cost + cur_dist < dist[(adj_node,service)]:
                new_path = list(path)
                new_path.append((adj_node, (bus,service)))
                #keep track of distance travelled
                new_total_distance = total_dist + cur_dist
                #push cost into dictionary
                newCost = cur_dist + curr_cost
                new_transfers = curr_transfers
                if (bus,service) != curr_service:
                    #cost for transfer very expensive to minimize transfer
                    newCost += cost_per_transfer
                    new_transfers += 1
                dist[(adj_node,(bus,service))] = newCost
                hq.heappush(heap, (newCost, new_total_distance, new_transfers, new_path))