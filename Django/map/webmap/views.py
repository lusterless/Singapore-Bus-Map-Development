from django.views.generic.base import TemplateView
from webmap.forms import HomeForm
from django.shortcuts import render
#import folium
#import ipywidgets
#from folium import plugins
#from folium.plugins import * 
import os
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import time

from webmap.overpassReq import *
from webmap.dijkstra import *


class HomeView(TemplateView):
    template_name = 'home.html'
    #load all nodes and edges of different graphs and store it in its respective variables
    walknodes, walkedges = importFiles('webmap/data/walkedges.geojson','webmap/data/walknodes.geojson')
    drivenodes, driveedges = importFiles('webmap/data/driveedges.geojson','webmap/data/drivenodes.geojson')
    lrtnodes, lrtedges = importFiles('webmap/data/lrtedges.geojson','webmap/data/lrtnodes.json')
    BusStops, busedges = importFiles('webmap/data/busedges.geojson','webmap/data/BusStops.geojson')
    """---------------------------------------------------------------------------------creating busmap---------------------------------------------------------------------------------"""
    G = ox.load_graphml("busGraph.graphml")
    """------------------------------------------------------------------------------------------------------------------------------------------------------------"""
    #load lrt stations
    with open('webmap/data/tograph.json') as f:
        lrtstation = json.load(f)
    #create graphs of walk and drive from exported graph files
    walkgraph = ox.load_graphml("walkGraph.graphml")
    drivegraph = ox.load_graphml("driveGraph.graphml")
    drive_graph_nodes = list(drivegraph.nodes.items())
    Gnodes = {}
    for items in drive_graph_nodes:
        Gnodes[items[0]] = items[1]
        
    def get(self, request):
        form = HomeForm()
        args = {'form': form, 'firstHalf': [],'secondHalf': [], 'transportroute': [], 'directions': "No Result", 'distances': "", "transfers": ""}
        return render(request, self.template_name, args)
        
    """---------------------------------------------------------------------------------Post requests---------------------------------------------------------------------------------"""
    def post(self, request):
        form = HomeForm(request.POST)
        if form.is_valid():
            travel = form.cleaned_data['travel']
            start = form.cleaned_data['start']
            end = form.cleaned_data['end']
            cost = form.cleaned_data['cost_per_transfer']
            origin = tuple(map(float, start.split(',')))
            dest = tuple(map(float, end.split(',')))
            #walking ------------------------------------------------------------------------------------
            if travel == "walking":
                start_node = ox.get_nearest_node(self.walkgraph, origin, method = 'haversine')
                end_node = ox.get_nearest_node(self.walkgraph, dest, method = 'haversine')
                coord_list,directions, distances = self.calculateShortest("","",origin,dest,str(start_node), str(end_node), travel, 0)
                coord_list.insert(0, list(origin))
                coord_list.append(list(dest))
                directions = "Walk:\nHead towards " + directions
                distances = "Distance: " + str(distances) + " metres away"
                coord_list_end = []
                transportRoute = []
                transferNo = ""
            #--------------------------------------------------------------------------------------------
            elif travel == "driving":
                start_node = ox.get_nearest_node(self.drivegraph, origin, method = 'haversine')
                end_node = ox.get_nearest_node(self.drivegraph, dest, method = 'haversine')
                coord_list, directions,distances = self.calculateShortest("","",origin,dest,str(start_node), str(end_node), travel, 0)
                coord_list.insert(0, list(origin))
                coord_list.append(list(dest))
                directions = "Walk:\nHead towards " + directions
                distances ="Distance: " + str(distances) + " metres away"
                transportRoute = []
                coord_list_end = []
                transferNo = ""
            elif travel == "train":
                start_node = ox.get_nearest_node(self.walkgraph, origin, method = 'haversine')
                end_node = ox.get_nearest_node(self.walkgraph, dest, method = 'haversine')
                startdist,startkey,startx,starty,startname = findNearestLrt(self.lrtstation, origin[0], origin[1])
                enddist,endkey,endx,endy,endname = findNearestLrt(self.lrtstation, dest[0], dest[1])
                coord_list, transportRoute, coord_list_end, directions, distances = self.calculateShortest((startdist,startkey,startx,starty,startname),(enddist,endkey,endx,endy,endname), origin,dest, start_node, end_node, travel,0)
                distances = "Distance: "+ str(distances) + " metres away"
                transferNo=""
                
            else:
                start_node = ox.get_nearest_node(self.walkgraph, origin, method = 'haversine')
                end_node = ox.get_nearest_node(self.walkgraph, dest, method = 'haversine')
                startBsCode ,startname, startx, starty = findNearestBusStop(self.BusStops, origin[0], origin[1])
                endBsCode ,endname,endx,endy = findNearestBusStop(self.BusStops, dest[0], dest[1])
                start_time = time.time()
                coord_list, transportRoute, coord_list_end, directions, distances, transferNo = self.calculateShortest((startBsCode ,startname, startx, starty),(endBsCode ,endname,endx,endy), origin,dest, start_node, end_node, travel, int(cost))
                if distances == 0:
                    distances = ""
                else:
                    distances = "Distance: " + str(distances) + " metres away"
                    
                if transferNo == 0:
                    transferNo = ""
                else:
                    transferNo = "Number of Transfers: " + str(transferNo-1)
                
        args =  {'form' : form, 'firstHalf': coord_list,'secondHalf': coord_list_end, 'transportroute': transportRoute, 'directions': directions, 'distances': distances, "transfers": transferNo}
        return render(request, self.template_name, args)
        
        
    def calculateShortest(self,starttransit,endtransit,origin,dest, start, end, mode, cost_per_transfer):
        if mode == "walking":
            path, distances = dijkstra(start,end, self.walkedges, self.walknodes)
            return convertToCoord(path, self.walknodes), convertToAddress(origin,dest,path, self.walknodes) , int(distances)
        elif mode == "driving":
            path, distances = dijkstra(start,end, self.driveedges, self.drivenodes)
            return convertToCoord(path, self.drivenodes),convertToAddress(origin,dest,path, self.drivenodes), int(distances)
        elif mode == "train":
            return self.transitCalculation(starttransit,endtransit,start,end,origin,dest)
        else:
            return self.calculateBus(starttransit,endtransit, start,end, origin, dest, cost_per_transfer)
        
    def calculateBus(self, starttransit,endtransit, start_node, end_node, origin, dest, cost_per_transfer):
        startBsCode ,startname, startx, starty = starttransit[0], starttransit[1], starttransit[2], starttransit[3]
        endBsCode ,endname,endx,endy = endtransit[0], endtransit[1], endtransit[2], endtransit[3]
        #calculate busRoute
        distances, transfers, path = dijkstra_for_bus(startBsCode,endBsCode,self.busedges, cost_per_transfer)
        #get bus stop coordinates
        bscoord = []
        directions = ""
        previous_service = ""
        for code, service in path: 
            try:
                bscoord.append([self.BusStops[code]['lat'],self.BusStops[code]['lon'],self.BusStops[code]['name']])
                if service == None:
                    directions +=  "\nBus:\nFrom " + self.BusStops[code]['name'] + ", Board bus " 
                else:
                    if endBsCode == code:
                        directions += "Alight at " + self.BusStops[code]['name'] + "\n"
                    elif previous_service == "" and service[0] != previous_service:
                        previous_service = service[0]
                        directions += service[0] + "\n" + self.BusStops[code]['name'] + "\n" 
                    elif service[0] != previous_service and previous_service != "":
                        previous_service = service[0]
                        directions += "\nSwitch to bus " + service[0] + " at " + self.BusStops[code]['name'] + "\n"
                    else:
                        directions += self.BusStops[code]['name'] + "\n"
            except KeyError as e:
                continue
        
        nearnode = []
        for item in bscoord:
            cod = (item[0],item[1])
            geom, u, v = ox.get_nearest_edge(self.G, cod)
            nn = min((u, v), key=lambda n: ox.great_circle_vec(cod[0],cod[1], self.G.nodes[n]['y'], self.G.nodes[n]['x']))
            nearnode.append(int(nn))
            
        #get directions for bus route ONLY by getting nearest edge -> nearest node between 2 end
                
        osmid = []
        for number in range(1, len(nearnode)):
            try:
                route = nx.shortest_path(self.drivegraph, source = nearnode[number-1], target = nearnode[number])
                osmid += route
            except:
                return [], [], [], "Bus goes out of map, Please try another method." , 0, 0
         
                
        converted_OSM_to_Coord = []
        for each in osmid:
            try:
                converted_OSM_to_Coord.append([self.Gnodes[each]['y'],self.Gnodes[each]['x']])
            except KeyError as e:
                continue 


        bs_fh_coord = (startx,starty)
        bs_first_half = ox.get_nearest_node(self.walkgraph,bs_fh_coord, method = 'haversine')
        pathfirst, firsthalfdist = dijkstra(str(start_node),str(bs_first_half),self.walkedges,self.walknodes)
        firstHalfDirection = "Walk:\nHead towards " + convertToAddress(origin,bs_fh_coord,pathfirst, self.walknodes)
        pathfirst = convertToCoord(pathfirst,self.walknodes)
        pathfirst.insert(0,list(origin))
        pathfirst.append(list(converted_OSM_to_Coord[0]))
    
        bs_eh_coord = (endx,endy)
        bs_endhalf = ox.get_nearest_node(self.walkgraph,bs_eh_coord, method = 'haversine')
        endpath, secondhalfdist = dijkstra(str(bs_endhalf),str(end_node),self.walkedges,self.walknodes)
        secondHalfDirection = "\nWalk:\nContinue towards " + convertToAddress(bs_eh_coord,dest,endpath, self.walknodes)
        endpath = convertToCoord(endpath,self.walknodes)
        endpath.insert(0, list(converted_OSM_to_Coord[-1]))
        endpath.append(list(dest))

        return pathfirst, converted_OSM_to_Coord, endpath, firstHalfDirection + directions + secondHalfDirection , int((distances*1000) + firsthalfdist +secondhalfdist), transfers
                    
    def transitCalculation(self, startlrt, endlrt,  start_node, end_node, origin, dest):
        startdist,startkey,startx,starty,startname = startlrt[0], startlrt[1], startlrt[2], startlrt[3], startlrt[4]
        enddist,endkey,endx,endy,endname = endlrt[0], endlrt[1], endlrt[2], endlrt[3], endlrt[4]
        lrtpath, lrtdistance = dijkstra(startkey, endkey, self.lrtedges, self.lrtnodes)
        lrtpath.append(endkey)
        #getting directions for LRT
        directions = ""
        index = 0
        counter = 0
        if startname == endname:
            directions = "\nWalk through " + startname + "\n"
        else:            
            for ids in lrtpath:
                if ids in self.lrtstation:
                    if index == 0 and counter == 0:
                        directions += "\nLRT:\nBoard at " + self.lrtstation[ids][2] + ", "
                        counter += 1
                    elif len(lrtpath)-1 == index:
                        directions += "Alight at " + self.lrtstation[ids][2] + "\n"
                    elif counter == 1:
                        directions += "Head towards " + self.lrtstation[ids][2] + ", "
                        counter += 1
                    else:
                        directions += self.lrtstation[ids][2] + ", "
                        counter += 1
                index+=1
        lrtpath = convertToCoord(lrtpath,self.lrtnodes)
        
        #start lrt coord
        lrt_fh_coord = (startx,starty)
        lrt_firsthalf = ox.get_nearest_node(self.walkgraph,lrt_fh_coord, method = 'haversine')
        pathfirst, firsthalfdist = dijkstra(str(start_node),str(lrt_firsthalf),self.walkedges,self.walknodes)
        firstHalfDirection = "Walk:\nHead towards " + convertToAddress(origin,lrt_fh_coord,pathfirst, self.walknodes)
        pathfirst = convertToCoord(pathfirst,self.walknodes)
        pathfirst.insert(0,list(origin))
        pathfirst.append(list(lrt_fh_coord))
        #end lrt coord
        lrt_eh_coord = (endx,endy)
        lrt_endhalf = ox.get_nearest_node(self.walkgraph,lrt_eh_coord, method = 'haversine')
        endpath, secondhalfdist = dijkstra(str(lrt_endhalf),str(end_node),self.walkedges,self.walknodes)
        secondHalfDirection = "\nWalk:\nContinue towards " + convertToAddress(lrt_eh_coord,dest,endpath, self.walknodes)
        endpath = convertToCoord(endpath,self.walknodes)
        endpath.append(list(dest))
        print(self.walknodes[str(lrt_firsthalf)][0]['lat'],self.walknodes[str(lrt_firsthalf)][0]['lon'])
        return pathfirst, lrtpath, endpath, firstHalfDirection + directions + secondHalfDirection , int(lrtdistance+ firsthalfdist +secondhalfdist)
        
        