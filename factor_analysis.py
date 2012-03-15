base = '/data/alstottj/Langley/'
from numpy import delete, empty, asarray, isnan, median, unique
from scipy.stats import skew, kruskal, ks_2samp

from rpy2 import robjects
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import FloatVector
stats = importr('stats')

#from Langley import database as db
import database as db
from Helix_database import Session, database_url
session = Session()
db.create_database(database_url)

import pickle
G = pickle.load(open(base+'Network_parents.p'))

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
plots = PdfPages(base+'Langley_distributions.pdf')

import powerlaw

dependents = ['Number_of_Children', 'Parent_Child_Registration_Interval_Corrected', 'Has_Children', 'Distance_from_Parent']
independents = ['Age', 'Gender', 'Relationship_with_Parent', 'Heard_Through_Medium', 'Same_Age_as_Parent',\
        'Same_City_as_Parent', 'Same_Country_as_Parent', 'Same_Gender_as_Parent', 'Same_Relationship_to_Parent_as_They_Had_to_Their_Parent',\
        'Heard_Through_Same_Medium_as_Parent']

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
    if 'parent_id' in n.keys():
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

#robjects.r("data<-read.table('%s')"%(base+'LangleyRtable'))
#robjects.r("attach(data)")

for d in dependents:
    print d
    for i in independents:
        print i
        dist = db.LangleyDistribution()
        dist.dependent = d
        dist.independent = i
        dist.factor = 'All'

        x = session.query(db.LangleyParticipant).values(getattr(db.LangleyParticipant, d))
        x = x[~isnan(x)]
        x = x[x>0]
        fit = powerlaw.Fit(x)
        dist.powerlaw = 0
        R1, p1 = fit.loglikelihood_ratio('power_law', 'exponential')
        R2, p2 = fit.loglikelihood_ratio('truncated_power_law', 'lognormal')
        if p1<.05 and p2<.05:
            dist.powerlaw = 1
        R3, p3 = fit.loglikelihood_ratio('power_law', 'lognormal')
        if p3<.05:
            dist.powerlaw = 2

        dist.mean = x.mean()
        dist.median = median(x)
        dist.skew = skew(x)

        session.add(dist)

        ax = plt.subplot(1,1,1)
        handles = {}

        if d=='Number_of_Children':
            y, x = powerlaw.cumulative_distribution_function(x, survival=True)
            handles['all'] = ax.plot(x, y, label="All")
            ax.set_xscale("log")
            ax.set_yscale("log")
            plt.title(d +' CDF, as a function of '+i)
            plt.xlabel(d)
            plt.ylabel('P(X)>x')
        else:
            handles['all'] = plt.hist(x, bins=100, histtype='step', label="All")
            ax.set_yscale("log")
            plt.title(d +' PDF as a function of '+i)
            plt.xlabel(d)
            plt.ylabel('P(X)')


        factors = unique(asarray(robjects.r(i)))
        for fn in range(len(factors)):
            dist = db.LangleyDistribution()
            dist.dependent = d
            dist.independent = i

            f = str(factors[fn])
            print f
            dist.factor = f

            x = asarray(robjects.r("%s[%s==%r]"%(d,i,f)))
            x = x[~isnan(x)]
            x = x[x>0]
            if not x.any():
                continue

            if d=='Number_of_Children':
                y, x = powerlaw.cumulative_distribution_function(x, survival=True)
                handles[str(f)] = ax.plot(x, y, label=str(f))
                ax.set_xscale("log")
                ax.set_yscale("log")
                plt.title(d +' CDF, as a function of '+i)
                plt.xlabel(d)
                plt.ylabel('P(X)>x')
                discrete=True
            else:
                handles[str(f)] = plt.hist(x, bins=100, histtype='step', label=str(f))
                ax.set_yscale("log")
                plt.title(d +' PDF as a function of '+i)
                plt.xlabel(d)
                plt.ylabel('P(X)')
            if d == 'Number_of_Children' or 'Interval' in d:
                discrete = True
            else:
                discrete = False

            fit = powerlaw.Fit(x, discrete=discrete)
            dist.powerlaw = 0
            R1, p1 = fit.loglikelihood_ratio('power_law', 'exponential')
            R2, p2 = fit.loglikelihood_ratio('truncated_power_law', 'lognormal')
            if p1<.05 and p2<.05:
                dist.powerlaw = 1
            R3, p3 = fit.loglikelihood_ratio('power_law', 'lognormal')
            if p3<.05:
                dist.powerlaw = 2

            dist.mean = x.mean()
            dist.median = median(x)
            dist.skew = skew(x)

            session.add(dist)

            other_factors = delete(factors, fn)
            n_other_factors = len(other_factors)
            p_krusk = empty(n_other_factors)
            D = empty(n_other_factors)
            p_KS = empty(n_other_factors)

            valid_other_factors = []
            Ds = []
            p_krusk = []
            p_KS = []
            for fn2 in range(n_other_factors):
                f2 = other_factors[fn2]
                y = asarray(robjects.r("%s[%s==%r]"%(d,i,f2)))
                y = y[~isnan(y)]
                if len(y)>2:
                    H, p_k = kruskal(x, y)
                    D, p_K = ks_2samp(x, y)
                    valid_other_factors.append(f2)
                    Ds.append(D)
                    p_krusk.append(p_k)
                    p_KS.append(p_K)

            #Adjust p values for multiple comparisons, then write
            p_krusk = stats.p_adjust(FloatVector(p_krusk), method = 'BH')
            p_KS = stats.p_adjust(FloatVector(p_KS), method = 'BH')

            for fn2 in range(len(valid_other_factors)):
                f2 = valid_other_factors[fn2]

                comp = db.LangleyDistributionCompare()
                comp.dependent = d
                comp.independent = i
                comp.factor1 = f
                comp.factor2 = f2

                comp.KW = p_krusk[fn2]
                comp.D = Ds[fn2]
                comp.KS = p_KS[fn2]
                session.add(comp)

            session.commit()

        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[::-1], labels[::-1], loc=9)
        plots.savefig()
        plt.close('all')
plots.close()
