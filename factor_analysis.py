base = '/data/alstottj/Langley/'
from numpy import asarray, isnan, median, unique
from scipy.stats import skew, kruskal, ks_2samp

#from rpy2 import robjects
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import FloatVector
stats = importr('stats')

import database as db
from Helix_database import Session, database_url
session = Session()
db.create_database(database_url)

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
plots = PdfPages(base+'Langley_distributions.pdf')

import powerlaw

dependents = ['Number_of_Children', 'Parent_Child_Registration_Interval_Corrected', 'Distance_from_Parent', 'Has_Children', 'Has_Parent']
independents = ['Age', 'Gender', 'Relationship_with_Parent', 'Heard_Through_Medium', 'Same_Age_as_Parent',\
        'Same_City_as_Parent', 'Same_Country_as_Parent', 'Same_Gender_as_Parent', 'Same_Relationship_to_Parent_as_They_Had_to_Their_Parent',\
        'Heard_Through_Same_Medium_as_Parent', 'Has_Parent']


#robjects.r("data<-read.table('%s')"%(base+'LangleyRtable'))
#robjects.r("attach(data)")

for d in dependents:
    print d
    if d == 'Has_Parent':
        independents = ['Age', 'Gender', 'Relationship_with_Parent', 'Heard_Through_Medium']
    else:
        independents = ['Age', 'Gender', 'Relationship_with_Parent', 'Heard_Through_Medium', 'Same_Age_as_Parent',\
                'Same_City_as_Parent', 'Same_Country_as_Parent', 'Same_Gender_as_Parent', 'Same_Relationship_to_Parent_as_They_Had_to_Their_Parent',\
                'Heard_Through_Same_Medium_as_Parent', 'Has_Parent']
    for i in independents:
        print i
        ax = plt.subplot(1,1,1)
        handles = {}
        factors = session.query(db.LangleyParticipant).values(getattr(db.LangleyParticipant, i))
        factors = unique([q for q in factors]).flatten()
        print factors
        factors = [q for q in factors if (q!=None and q!='unknown' and q!='0')]
        print factors
        n_factors = len(factors)
        if n_factors<2:
            continue

        fs = []
        f2s = []
        Ds = []
        p_krusks = []
        p_KSs = []
        skews = []
        medians = []
        for fn in range(-1, n_factors):
            dist = db.LangleyDistribution()
            dist.dependent = d
            dist.independent = i

            if fn==-1:
                f='All'
                data = session.query(db.LangleyParticipant).\
                values(getattr(db.LangleyParticipant, d))
            else:
                f = factors[fn]
                data = session.query(db.LangleyParticipant).\
                filter(getattr(db.LangleyParticipant, i)==f).\
                values(getattr(db.LangleyParticipant, d))
            dist.factor = str(f)

            data = [q for q in data if q[0]!=None]
            data = asarray([q for q in data if ~isnan(q)]).flatten()
            print str(f)+' '+str(len(data))+' cases'
            if len(data)<2:
                print "Skipping due to too few cases"
                continue

            if d=='Number_of_Children':
                y, x = powerlaw.cumulative_distribution_function(data, survival=True)
                if f=='All':
                    handles[str(f)] = ax.plot(x, y, label=str(f), linewidth=4, color='k')
                else:
                    handles[str(f)] = ax.plot(x, y, label=str(f))
                ax.set_xscale("log")
                ax.set_yscale("log")
                plt.title(d +' CDF, as a function of '+i)
                plt.xlabel(d)
                plt.ylabel('P(X)>x')
            else:
                if f=='All':
                    handles[str(f)] = plt.hist(data, bins=100, histtype='step', label=str(f), color='k')
                else:
                    handles[str(f)] = plt.hist(data, bins=100, histtype='step', label=str(f))
                ax.set_yscale("log")
                plt.title(d +' PDF as a function of '+i)
                plt.xlabel(d)
                plt.ylabel('P(X)')
            if d == 'Number_of_Children' or d == 'Has_Children':
                discrete = True
            else:
                discrete = False

            if d not in ['Has_Children', 'Has_Parent']:
                fit = powerlaw.Fit(data, discrete=discrete)
                R1, p1 = fit.loglikelihood_ratio('power_law', 'exponential')
                R2, p2 = fit.loglikelihood_ratio('truncated_power_law', 'lognormal')
                R3, p3 = fit.loglikelihood_ratio('power_law', 'lognormal')
                if p1>.05:
                    dist.powerlaw = 0
                else:
                    dist.powerlaw = 1
                if p2<.05:
                    dist.powerlaw = 2
                if p3<.05:
                    dist.powerlaw = 3

            dist.mean = data.mean()
            dist.median = median(data)
            dist.skew = skew(data)

            session.add(dist)

            if f=='All':
                continue

            for fn2 in range(fn+1, n_factors):
                f2 = factors[fn2]
                data_other = session.query(db.LangleyParticipant).filter(getattr(db.LangleyParticipant, i)==f2).values(getattr(db.LangleyParticipant, d))
                data_other = [q for q in data_other if q[0]!=None]
                data_other = asarray([q for q in data_other if ~isnan(q)]).flatten()
                if len(data_other)>2:
                    H, p_krusk = kruskal(data, data_other)
                    D, p_KS = ks_2samp(data/median(data), data_other/median(data_other))
                    fs.append(f)
                    f2s.append(f2)
                    Ds.append(D)
                    p_krusks.append(p_krusk)
                    p_KSs.append(p_KS)
                    skews.append(skew(data)-skew(data_other))
                    medians.append(median(data)-median(data_other))

            #Adjust p values for multiple comparisons, then write
        p_krusks = asarray(stats.p_adjust(FloatVector(p_krusks), method = 'holm'))
        p_KSs = asarray(stats.p_adjust(FloatVector(p_KSs), method = 'holm'))
        print fs

        for q in range(len(fs)):
            f = fs[q]
            f2 = f2s[q]

            comp = db.LangleyDistributionCompare()
            comp.dependent = d
            comp.independent = i
            comp.factor1 = f
            comp.factor2 = f2

            comp.KW = p_krusks[q]
            comp.D = Ds[q]
            comp.KS = p_KSs[q]
            comp.skew = skews[q]
            comp.median = medians[q]
            session.add(comp)


            session.commit()

        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[::-1], labels[::-1], loc=1)
        plots.savefig()
        plt.close('all')
plots.close()
