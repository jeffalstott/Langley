base = '/data/alstottj/Langley/'
import pickle
G = pickle.load(open(base+'Network.p'))
for n_id in G.node:
    n = G.node[n_id]
    G.add_node(n_id, node_id = n_id)
    if n['depth']>0:
        p = G.node[n['parent_id']]
        G.add_node(n_id, parent_age = p['age'], parent_city = p['city'], parent_country = p['country'],\
                parent_gender = p['gender'], parent_wait_time = p['wait_time'], parent_source_from = p['source_from'],\
                parent_source_through = p['source_through'], parent_sigma = p['sigma'], parent_join_time = p['join_time'])
#Include flags for same demographics
        G.add_node(n_id, same_age = (n['age']==p['age'])) 
        G.add_node(n_id, same_city = (n['city']==p['city']))
        G.add_node(n_id, same_gender = (n['gender']==p['gender']))
        G.add_node(n_id, same_country = (n['country']==p['country']))
        G.add_node(n_id, same_source_from = (n['source_from']!=0 and n['source_from']==p['source_from']))
        G.add_node(n_id, same_source_relationship= (n['source_through']!=0 and n['source_through']==p['source_through']))
        G.add_node(n_id, has_children = G.out_degree()[n_id]>0) 

pickle.dump(G, open('/data/alstottj/Langley/Network_parents.p', 'w'))
