base = '/data/alstottj/Langley/'
from numpy import delete, empty, asarray, isnan, median, unique
from scipy.stats import skew, kruskal, ks_2samp

#from rpy2 import robjects
#from rpy2.robjects.packages import importr
#from rpy2.robjects.vectors import FloatVector
#stats = importr('stats')

import database as db
from Helix_database import Session, database_url
session = Session()
db.create_database(database_url)

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
plots = PdfPages(base+'Langley_distributions.pdf')

import powerlaw

dependents = ['Number_of_Children', 'Parent_Child_Registration_Interval_Corrected', 'Has_Children', 'Distance_from_Parent']
independents = ['Has_Parent', 'Age', 'Gender', 'Relationship_with_Parent', 'Heard_Through_Medium', 'Same_Age_as_Parent',\
        'Same_City_as_Parent', 'Same_Country_as_Parent', 'Same_Gender_as_Parent', 'Same_Relationship_to_Parent_as_They_Had_to_Their_Parent',\
        'Heard_Through_Same_Medium_as_Parent']


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

        data = session.query(db.LangleyParticipant).values(getattr(db.LangleyParticipant, d))
        data = [q for q in data if q[0]!=None]
        data = asarray([q for q in data if ~isnan(q)]).flatten()

        if d == 'Number_of_Children':
            discrete = True
        else:
            discrete = False
        fit = powerlaw.Fit(data, discrete=discrete)
        R1, p1 = fit.loglikelihood_ratio('power_law', 'exponential')
        R2, p2 = fit.loglikelihood_ratio('truncated_power_law', 'lognormal')
        if p1>.05 or p2>.05:
            dist.powerlaw = 0
        if p1<.05 and p2<.05:
            dist.powerlaw = 1
        R3, p3 = fit.loglikelihood_ratio('power_law', 'lognormal')
        if p3<.05:
            dist.powerlaw = 2

        dist.mean = data.mean()
        dist.median = median(data)
        dist.skew = skew(data)

        session.add(dist)

        ax = plt.subplot(1,1,1)
        handles = {}

        if d=='Number_of_Children':
            y, x = powerlaw.cumulative_distribution_function(data, survival=True)
            handles['all'] = ax.plot(x, y, label="All")
            ax.set_xscale("log")
            ax.set_yscale("log")
            plt.title(d +' CDF, as a function of '+i)
            plt.xlabel(d)
            plt.ylabel('P(X)>x')
        else:
            handles['all'] = plt.hist(data, bins=100, histtype='step', label="All")
            ax.set_yscale("log")
            plt.title(d +' PDF as a function of '+i)
            plt.xlabel(d)
            plt.ylabel('P(X)')


        factors = session.query(db.LangleyParticipant).values(getattr(db.LangleyParticipant, i))
        factors = unique([q for q in factors]).flatten()
        for fn in range(len(factors)):
            dist = db.LangleyDistribution()
            dist.dependent = d
            dist.independent = i

            f = factors[fn]
            dist.factor = str(f)

#            x = asarray(robjects.r("%s[%s==%r]"%(d,i,f)))
            data = session.query(db.LangleyParticipant).\
            filter(getattr(db.LangleyParticipant, i)==f).values(getattr(db.LangleyParticipant, d))
            data = [q for q in data if q[0]!=None]
            data = asarray([q for q in data if ~isnan(q)]).flatten()
            print str(f)+' '+str(len(data))+' cases'
            if len(data)<2:
                print "Skipping due to too few cases"
                continue

            if d=='Number_of_Children':
                y, x = powerlaw.cumulative_distribution_function(data, survival=True)
                handles[str(f)] = ax.plot(x, y, label=str(f))
                ax.set_xscale("log")
                ax.set_yscale("log")
                plt.title(d +' CDF, as a function of '+i)
                plt.xlabel(d)
                plt.ylabel('P(X)>x')
            else:
                handles[str(f)] = plt.hist(data, bins=100, histtype='step', label=str(f))
                ax.set_yscale("log")
                plt.title(d +' PDF as a function of '+i)
                plt.xlabel(d)
                plt.ylabel('P(X)')
            if d == 'Number_of_Children':
                discrete = True
            else:
                discrete = False

            fit = powerlaw.Fit(data, discrete=discrete)
            dist.powerlaw = 0
            R1, p1 = fit.loglikelihood_ratio('power_law', 'exponential')
            R2, p2 = fit.loglikelihood_ratio('truncated_power_law', 'lognormal')
            if p1<.05 and p2<.05:
                dist.powerlaw = 1
            R3, p3 = fit.loglikelihood_ratio('power_law', 'lognormal')
            if p3<.05:
                dist.powerlaw = 2

            dist.mean = data.mean()
            dist.median = median(data)
            dist.skew = skew(data)

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
                data_other = session.query(db.LangleyParticipant).filter(getattr(db.LangleyParticipant, i)==f2).values(getattr(db.LangleyParticipant, d))
                data_other = [q for q in data_other if q[0]!=None]
                data_other = asarray([q for q in data_other if ~isnan(q)]).flatten()
                print str(f2)+' '+str(len(y))+' cases'
                if len(y)>2:
                    H, p_k = kruskal(data, data_other)
                    D, p_K = ks_2samp(data, data_other)
                    valid_other_factors.append(f2)
                    Ds.append(D)
                    p_krusk.append(p_k)
                    p_KS.append(p_K)

            #Adjust p values for multiple comparisons, then write
#            p_krusk = stats.p_adjust(FloatVector(p_krusk), method = 'BH')
#            p_KS = stats.p_adjust(FloatVector(p_KS), method = 'BH')

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
        ax.legend(handles[::-1], labels[::-1], loc=1)
        plots.savefig()
        plt.close('all')
plots.close()
