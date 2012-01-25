import csv
import sys
import datetime
import numpy
import networkx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import statistics
from time import sleep
from googlemaps import GoogleMaps
api_key = 'ABQIAAAAqEio4fjGXzOaNqtV-4JI6hTuiPxMM29R6K22C2e3kxpENlzcIRSG2voiQVRMmRtRcNMp6ujQaSSBbA'
gmaps = GoogleMaps(api_key)
from geopy import geocoders
geo = geocoders.Google()
#geo = geocoders.MediaWiki("http://wiki.case.edu/%s")
#geo = geocoders.SemanticMediaWiki("http://wiki.case.edu/%s", attributes=['Coordinates'], relations=['Located in'])
#geo = geocoders.Yahoo('3vfbwW_V34H3Dy2CaPO0_BIRtP5hzanCckWHt2T7Xv8FCE0IXk1rqkvh1KBS4HZ_L_I-')

#Define helper functions
find_key = lambda x, y: [k for k, v in x.iteritems() if v == y]
def plot_distribution(variable, name, x_label, xmin=None):
    print("Calculating "+name)
    iCDF, bins = statistics.cumulative_distribution_function(variable, survival=True, xmin=xmin)
    plt.plot(bins, iCDF)
    plt.gca().set_xscale("log")
    plt.gca().set_yscale("log")
    plt.title(name +' survival function')
    plt.xlabel(x_label)
    plt.ylabel('P(X)>x')
    plots.savefig()
    plt.close('all')

#    plt.hist(variable, bins=100, normed=True)
#    plt.title(name +' histogram')
#    plt.xlabel(x_label)
#    plt.ylabel('P(X)')
#    plots.savefig()
#   plt.close('all')

import math

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

#Initialize plots and data
plots = PdfPages('Langley.pdf')

data = csv.reader(open('participants.csv'))
connections = numpy.zeros((1090,1090))
G = networkx.DiGraph()
G.gender = {}
G.age = {}
G.country = {}
G.city = {}
G.lat = {}
G.lng = {}
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
            lat=None
            lng=None
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
                    lat=None
                    lng=None
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
            

#Calculate wait times
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
        distance = None

    G.add_edge(parent_id, child_id, wait_time=wait_time, distance=distance)
    G.add_node(child_id, wait_time=wait_time, parent_id=parent_id, distance=distance)

#Calculate depths and sigmas
def calculate_depths(node, depth):
    G.add_node(node, depth=depth, sigma = G.out_degree(node))
    for n in G.successors(node):
        calculate_depths(n, depth+1)

for n in G.origins:
    calculate_depths(n, 0)

output_file = open('Langley.csv', 'wb')
CSV_labels = ['node_id', 'age', 'city', 'country', 'depth', 'gender', 'sigma', 'source_from', 'source_through', 'wait_time',\
        'parent_id', 'parent_age', 'parent_city', 'parent_country', 'parent_gender', 'parent_sigma', 'parent_source_from', 'parent_source_through','parent_wait_time',\
        'same_age', 'same_city', 'same_country', 'same_gender', 'same_source_from', 'same_source_through','same_source']
csv_output = csv.writer(output_file)
csv_output.writerow(CSV_labels)
csv_output = csv.DictWriter(output_file, CSV_labels, restval='', extrasaction='ignore')

#Encode parent information in each node and write the node's info to a CSV file
for n_id in G.node:
    n = G.node[n_id]
    G.add_node(n_id, node_id = n_id)
    if n['depth']>0:
        p = G.node[n['parent_id']]
        G.add_node(n_id, parent_age = p['age'], parent_city = p['city'], parent_country = p['country'],\
                parent_gender = p['gender'], parent_wait_time = p['wait_time'], parent_source_from = p['source_from'],\
                parent_source_through = p['source_through'], parent_sigma = p['sigma'])
#Include flags for same demographics
        G.add_node(n_id, same_age = (n['age']==p['age'])) 
        G.add_node(n_id, same_city = (n['city']==p['city']))
        G.add_node(n_id, same_gender = (n['gender']==p['gender']))
        G.add_node(n_id, same_country = (n['country']==p['country']))
        G.add_node(n_id, same_source_from = (n['source_from']!=0 and n['source_from']==p['source_from']))
        G.add_node(n_id, same_source_through= (n['source_through']!=0 and n['source_through']==p['source_through']))
    csv_output.writerow(n)

f=open('Langley.txt', 'w')

f.write('Number of participants: %.2f'%G.number_of_nodes())
f.write('\nNumber of connections: %.2f'%G.number_of_edges())
f.write('\n')

C=networkx.connected_component_subgraphs(G.to_undirected())
team_sizes = numpy.zeros(len(C))
for i in range(len(C)):
    team_sizes[i] = networkx.number_of_nodes(C[i])
f.write('\nNumber of teams: %.2f'%len(team_sizes))
f.write('\nNumber of teams larger than 1: %.2f'%sum(team_sizes>1))
f.write('\nMean team size: %.2f'%numpy.mean(team_sizes))
f.write('\nMean team size larger than 1: %.2f'%team_sizes[team_sizes>1].mean())

f.write('\n')
depths = numpy.array(networkx.get_node_attributes(G, 'depth').values())
f.write('\nMean depth: %.2f'%numpy.mean(depths))
depths1 = numpy.concatenate((depths[depths>0], numpy.zeros(sum(team_sizes>1))))
f.write('\nMean depth in teams larger than 1: %.2f'%numpy.mean(depths1))
f.write('\n')
f.write('\nAssortativity of gender: %.2f'%networkx.attribute_assortativity(G,'gender'))
f.write('\nAssortativity of country: %.2f'%networkx.attribute_assortativity(G,'country'))
f.write('\nAssortativity of city: %.2f'%networkx.attribute_assortativity(G,'city'))
f.write('\nAssortativity of age: %.2f'%networkx.attribute_assortativity(G,'age'))
f.write('\nAssortativity of source_from: %.2f'%networkx.attribute_assortativity(G,'source_from'))
f.write('\nAssortativity of source_through: %.2f'%networkx.attribute_assortativity(G,'source_through'))


genders= networkx.get_node_attributes(G, 'gender')
females = find_key(genders, 'female')
males = find_key(genders, 'male')
neuters = find_key(genders, 'unknown')

ages = networkx.get_node_attributes(G, 'age')
media1 = networkx.get_edge_attributes(G, 'source_from')
media2 = networkx.get_edge_attributes(G, 'source_through')
countries = networkx.get_node_attributes(G, 'country')
f.write('\n')

sigmas = G.out_degree().values()
mean_sigma = numpy.mean(sigmas)
f.write('\nMean sigma: %.2f'%mean_sigma)
f.write('\nMean sigma males: %.2f'%numpy.mean([G.out_degree(i) for i in males]))
f.write('\nMean sigma females: %.2f'%numpy.mean([G.out_degree(i) for i in females]))
f.write('\nMean sigma unknowns genders: %.2f'%numpy.mean([G.out_degree(i) for i in neuters]))

f.write('\nMean sigma age group 1: %.2f'%numpy.mean([G.out_degree(i) for i in find_key(ages, 1)]))
f.write('\nMean sigma age group 2: %.2f'%numpy.mean([G.out_degree(i) for i in find_key(ages, 2)]))
f.write('\nMean sigma age group 3: %.2f'%numpy.mean([G.out_degree(i) for i in find_key(ages, 3)]))
f.write('\nMean sigma age group 4: %.2f'%numpy.mean([G.out_degree(i) for i in find_key(ages, 4)]))
f.write('\nMean sigma age group unknown: %.2f'%numpy.mean([G.out_degree(i) for i in find_key(ages, 'unknown')]))

f.write('\nMean sigma when invited through media source 1: %.2f'%numpy.mean([G.out_degree(i[1]) for i in find_key(media1,1)+find_key(media2,1)]))
f.write('\nMean sigma when invited through media source 2: %.2f'%numpy.mean([G.out_degree(i[1]) for i in (find_key(media1,2)+find_key(media2,2))]))
f.write('\nMean sigma when invited through media source 3: %.2f'%numpy.mean([G.out_degree(i[1]) for i in (find_key(media1,3)+find_key(media2,3))]))
f.write('\nMean sigma when invited through media source 4: %.2f'%numpy.mean([G.out_degree(i[1]) for i in (find_key(media1,4)+find_key(media2,4))]))
f.write('\nMean sigma when invited through media source 5: %.2f'%numpy.mean([G.out_degree(i[1]) for i in (find_key(media1,5)+find_key(media2,5))]))
f.write('\nMean sigma when invited through media source 6: %.2f'%numpy.mean([G.out_degree(i[1]) for i in (find_key(media1,6)+find_key(media2,6))]))
f.write('\nMean sigma when invited through media source unknown: %.2f'%numpy.mean([G.out_degree(i[1]) for i in (find_key(media1,0)+find_key(media2,0))]))

f.write('\n')
wait_times = networkx.get_edge_attributes(G, 'wait_time').values()
f.write('\nMean wait time: %.2f'%numpy.mean(wait_times))
from numpy import where, asarray
distances = asarray(networkx.get_edge_attributes(G, 'distance').values())
f.write('\nMean distance: %.2f'%numpy.mean(distances[where(distances)]))

signups = networkx.get_node_attributes(G, 'join_time').values()
signups.sort()
inter_signup_times = [signups[i]-signups[i-1] for i in range(1, len(signups))]
inter_signup_times = [x.seconds+(x.days*60*60*24) for x in inter_signup_times]
f.write('\nMean inter-signup time: %.2f'%numpy.mean(inter_signup_times))
f.close()

plot_distribution(team_sizes, 'Team sizes', 'Team size')
plot_distribution(sigmas, 'Branching ratio', 'Branching ratio (Sigma')
plot_distribution(depths, 'Network depth', 'Network depth')
plot_distribution(inter_signup_times, 'Inter-signup times', 'Inter-signup times (seconds between individuals joining the website)')
plot_distribution(wait_times, 'Wait times', 'Wait times (seconds from invitation to joining)', xmin=0)
plt.hist(wait_times, bins=100, normed=True)
plt.title('Wait times histogram')
plt.xlabel('Wait times (seconds from invitation to joining)')
plt.ylabel('P(X)')
plots.savefig()
plt.close('all')
plot_distribution(distances, 'Distances', 'Distances (km between individual and recruit)', xmin=0)
plt.hist(distances[where(distances)], bins=100, normed=True)
plt.title('Distances histogram')
plt.xlabel('Distances (km between individual and recruit')
plt.ylabel('P(X)')
plots.savefig()
plt.close('all')

#print("Plotting graph")
#pos=networkx.spring_layout(G.to_undirected())
gender_colors = []
for i in G.gender:
    if G.gender[i]=='male':
        gender_colors.append('blue')
    elif G.gender[i]=='female':
        gender_colors.append('red')
    elif G.gender[i]=='unknown':
        gender_colors.append('green')
#networkx.draw(G,pos,node_size=20,alpha=0.5,with_labels=False,\
#        node_color=gender_colors)
#plt.title("Team networks, colored by gender")
#plots.savefig()
#plt.close('all')

age_colors = []
for i in G.age:
    if G.age[i]==1:
        age_colors.append('red')
    elif G.age[i]==2:
        age_colors.append('blue')
    elif G.age[i]==3:
        age_colors.append('green')
    elif G.age[i]==4:
        age_colors.append('yellow')
    elif G.age[i]=='unknown':
        age_colors.append('black')

#networkx.draw(G,pos,node_size=20,alpha=0.5,with_labels=False,\
#        node_color = age_colors)
#plt.title("Team networks, colored by age group")
#plots.savefig()
#plt.close('all')
plots.close()
