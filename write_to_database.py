base = '/data/alstottj/Langley/'

import pickle
G = pickle.load(open(base+'Network_parents.p'))

import database as db
from Helix_database import Session, database_url
session = Session()
db.create_database(database_url)

for n_id in G.node:
    n = G.node[n_id]
    p = db.LangleyParticipant()
    p.node_id = n['node_id']
    p.Age = n['age']
    p.City = n['city']
    p.Country = n['country']
    p.Depth_in_Invite_Chain = n['depth']
    p.Gender = n['gender']
    p.Number_of_Children = n['sigma']
    p.Has_Children = (G.out_degree()[n_id]>0)
    p.Relationship_with_Parent = n['source_from']
    p.Heard_Through_Medium = n['source_through']
    p.Join_Time = n['join_time']
    p.Latitude = n['lat']
    p.Longitude = n['lng']
    p.Has_Parent = False
    if 'parent_id' in n.keys():
        p.Has_Parent = True
        p.parent_id = n['parent_id']
        p.Parent_Child_Registration_Interval = n['wait_time']
        p.Parent_Child_Registration_Interval_Corrected = max(n['wait_time'], 0)
        p.Distance_from_Parent = n['distance']
        p.Parent_Age = n['parent_age']
        p.Parent_City = n['parent_city']
        p.Parent_Country = n['parent_country']
        p.Parent_Gender = n['parent_gender']
        p.Parent_Number_of_Children = n['parent_sigma']
        p.Parent_Relationship_with_Grandparent = n['parent_source_from']
        p.Parent_Heard_Through_Medium = n['parent_source_through']
        p.Grandparent_Parent_Registration_Interval = n['parent_wait_time']
        p.Same_Age_as_Parent = n['same_age']
        p.Same_City_as_Parent = n['same_city']
        p.Same_Country_as_Parent = n['same_country']
        p.Same_Gender_as_Parent = n['same_gender']
        p.Same_Relationship_to_Parent_as_They_Had_to_Their_Parent = n['same_source_from']
        p.Heard_Through_Same_Medium_as_Parent = n['same_source_through']
        p.Parent_Join_Time = n['parent_join_time']
    session.add(p)
session.commit()
