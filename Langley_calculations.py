import csv
import sys
import datetime
import numpy
import networkx
import math
from time import sleep
from googlemaps import GoogleMaps
api_key = 'ABQIAAAAqEio4fjGXzOaNqtV-4JI6hTuiPxMM29R6K22C2e3kxpENlzcIRSG2voiQVRMmRtRcNMp6ujQaSSBbA'
gmaps = GoogleMaps(api_key)
from geopy import geocoders
geo = geocoders.Google()

#Define helper function
def distance_on_unit_sphere(lat1, long1, lat2, long2):

    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
        
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
        
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
        
    # Compute spherical distance from spherical coordinates.
        
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc
data = csv.reader(open('participants.csv'))
connections = numpy.zeros((1090,1090))
G = networkx.DiGraph()
G.gender = {}
G.age = {}
G.country = {}
G.city = {}
G.lat = {}
G.lng = {}
G.distance = {}
G.wait_time = {}
G.join_time = {}
G.origins = []
i = 0

#Construct the network
for line in data:
    if line[0]!='id':
        i = i+1
        child_id = int(line[0])-1000

#Add geographic and time information
        G.country[i] = line[20]
        G.city[i] = line[21]
        G.join_time[i] = datetime.datetime.strptime(line[19], "%Y-%m-%d %H:%M:%S")
        
#Code for gender
        if line[13]=='M':
            G.gender[child_id] = 'male'
        elif line[13]=='F':
            G.gender[child_id] = 'female'
        else:
            G.gender[child_id] = 'unknown'

#Code for age group
        if line[14]!='':
            G.age[i] = int(line[14])
        else:
            G.age[i] = 'unknown'

#Parse sources
        source_from = 0
        source_through = 0
        if line[7]!='':
            source_from = int(line[7])
        if line[9]!='':
            source_through = int(line[9])
        #Only the first dozen or so participants had a source listed in the third column (I imagine this is a parsing error upstream of my analysis). All but one of those had just one source reported, and that one had THREE sources listed. I'm effectively ignoring the third source given by that single individual, in order to make the dataset simpler. If there's a response in column 3, we treat it as a response in column 1.
        if line[11]!='':
            source_through = int(line[11])

#Create node
        country = line[20]
        city = line[21]
        if country=='':
            lat=False
            lng=False
        else:
            try:
                place, (lat, lng) = geo.geocode(city+' '+country, exactly_one=False)[0]
                sleep(3)
            except:
                print sys.exc_info()[0]
                try:
                    place, (lat, lng) = geo.geocode(country, exactly_one=False)[0]
                    sleep(3)
                except:
                    print sys.exc_info()[0]
                    print str(child_id)+': '+city+', '+country
                    lat=False
                    lng=False
        G.lat[child_id]=lat
        G.lng[child_id]=lng

        G.add_node(child_id, gender=G.gender[i], age=G.age[i],\
                country=country, city=city,lat=lat, lng=lng,\
                join_time=datetime.datetime.strptime(line[19], "%Y-%m-%d %H:%M:%S"),\
                source_from=source_from, source_through=source_through,\
                wait_time = 0)

#Add connections, if they exist
        if line[1]!='0':
            parent_id = int(line[1])-1000
            G.add_edge(parent_id, child_id, source_from=source_from, source_through=source_through)
            
            connections[parent_id,child_id]=1
        else:
            G.origins.append(i)
            

#Calculate wait times and distances
for e in G.edges():
    parent_id = e[0]
    child_id = e[1]
    wait_time = G.join_time[child_id]-G.join_time[parent_id]
    wait_time = wait_time.seconds+(wait_time.days*60*60*24)

    if G.lat[parent_id] and G.lat[child_id]:
        parent_lat = G.lat[parent_id]
        parent_lng = G.lng[parent_id]
        child_lat = G.lat[child_id]
        child_lng = G.lng[child_id]
        distance = distance_on_unit_sphere(parent_lat, parent_lng, child_lat, child_lng)
        distance = distance*6373.
    else:
        distance = False

    G.add_edge(parent_id, child_id, wait_time=wait_time, distance=distance)
    G.add_node(child_id, wait_time=wait_time, parent_id=parent_id, distance=distance)

#Calculate depths and sigmas
def calculate_depths(node, depth):
    G.add_node(node, depth=depth, sigma = G.out_degree(node))
    for n in G.successors(node):
        calculate_depths(n, depth+1)

for n in G.origins:
    calculate_depths(n, 0)
