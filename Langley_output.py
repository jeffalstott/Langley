import pickle
import csv
import networkx
import statistics
import numpy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

#Helper function
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

#Initialize plots
plots = PdfPages('Langley.pdf')

#Load data
G = pickle.load(open('/data/alstottj/Langley/Network.p'))

output_file = open('Langley.csv', 'wb')
CSV_labels = ['node_id', 'age', 'city', 'country', 'depth', 'gender', 'sigma', 'source_from', 'source_through', 'wait_time', 'distance',\
        'parent_id', 'parent_age', 'parent_city', 'parent_country', 'parent_gender', 'parent_sigma', 'parent_source_from', 'parent_source_through','parent_wait_time',\
        'same_age', 'same_city', 'same_country', 'same_gender', 'same_source_from', 'same_source_through']
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
