# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# Initial Setup
# --------

# <codecell>

cd /data/alstottjd/Langley/

# <codecell>

figures = []
fn = 1
sfn = 1

# <codecell>

matplotlib.rc('font', **{'sans-serif' : 'Arial', 
                         'family' : 'sans-serif',
                         'size' : 10})

from matplotlib.font_manager import FontProperties

panel_label_font = FontProperties().copy()
panel_label_font.set_weight("bold")
panel_label_font.set_size(12.0)
panel_label_font.set_family("sans-serif")

# <markdowncell>

# Load teams
# --------

# <codecell>

import networkx
import pickle
G = pickle.load(open('/data/alstottjd/Langley/Network_parents.p'))
C=networkx.connected_component_subgraphs(G.to_undirected())

# <codecell>

for i in range(len(C)):
    C[i] = G.subgraph(C[i].nodes())

# <codecell>

def max_depth(G):
    d = 0
    for i in G.node:
        d = max(d,G.node[i]['depth'])
    return float(d)

# <markdowncell>

# Figure 1: Example Team and Team Statistics
# ----

# <codecell>

figwidth = 8.6

fig = plt.figure(figsize=(figwidth, figwidth/(2*1.618)))



######
ax = fig.add_subplot(131)

import matplotlib.cm as cm

i = 3 #Picked team number 3

        
d = max_depth(C[i])

depth_colors = []
for j in C[i].nodes():
    depth_percentage = C[i].node[j]['depth']/d
    depth_colors.append(cm.gray(depth_percentage))
    
same_age_colors = []
same_media_colors = []
same_relationship_colors = []
for e in C[i].edges():
    if C[i].node[e[0]]['age']=='unknown' or C[i].node[e[1]]['age']=='unknown':
        same_age_colors.append('green')
    elif C[i].node[e[0]]['age']==C[i].node[e[1]]['age']:
        same_age_colors.append('blue')
    else:
        same_age_colors.append('red')
    if C[i].node[e[0]]['source_through']==0 or C[i].node[e[1]]['source_through']==0:
        same_media_colors.append('green')
    elif C[i].node[e[0]]['source_through']==C[i].node[e[1]]['source_through']:
        same_media_colors.append('blue')
    else:
        same_media_colors.append('red')
    if C[i].node[e[0]]['source_from']==0 or C[i].node[e[1]]['source_from']==0:
        same_relationship_colors.append('green')
    elif C[i].node[e[0]]['source_from']==C[i].node[e[1]]['source_from']:
        same_relationship_colors.append('blue')
    else:
        same_relationship_colors.append('red')

node_size = 50
alpha = 1
width = .5

#title("Example team, %i members, %.0f generations"%(len(C[i].node), d))
H = C[i].copy()
for n in H.node:
    for k in H.node[n].keys():
        H.node[n].pop(k)
#pos=networkx.spring_layout(C[i].to_undirected())
pos=networkx.graphviz_layout(H,prog='dot')
#pos=networkx.graphviz_layout(C[i],prog="twopi",root=0)


networkx.draw(C[i],pos,node_size=node_size,
    alpha=alpha, width=width, 
    with_labels=False, 
    node_color = depth_colors,
    edge_color = same_relationship_colors, 
    arrows=True,
    ax=ax)

# adjust the plot limits
cut = 1.15
xmax= cut*max(xx for xx,yy in pos.values())
xmin= cut*min(xx for xx,yy in pos.values())
ymax= cut*max(yy for xx,yy in pos.values())
ymin= cut*min(yy for xx,yy in pos.values())
#ax.set_xlim(xmin,xmax)
#ax.set_ylim(ymin,ymax)

yl = ax.set_ylabel("")
ax.annotate("A", (0,1.), xycoords=(yl, "axes fraction"), 
             fontproperties=panel_label_font) 


#######
s = 50
import powerlaw

team_sizes = numpy.zeros(len(C))
for i in range(len(C)):
    team_sizes[i] = networkx.number_of_nodes(C[i])
sizes_fit = powerlaw.Fit(team_sizes, discrete=True)

number_of_children = asarray(G.out_degree().values())
number_of_children = number_of_children[number_of_children>0]
num_children_fit = powerlaw.Fit(number_of_children, discrete=True)

########
ax = fig.add_subplot(132)
x,y = sizes_fit.ccdf(original_data=True)
ax.scatter(x,y, s=s)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("Team Size")
yl = ax.set_ylabel(u"p(X \u2265 x)")
ylim(10**-3,1)
xlim(1, 10**3)
ax.annotate("B", (0,1.), xycoords=(yl, "axes fraction"), 
             fontproperties=panel_label_font) 

print(sizes_fit.alpha)
print(sizes_fit.xmin)
print(sizes_fit.loglikelihood_ratio('power_law', 'exponential'))
print(sizes_fit.loglikelihood_ratio('power_law', 'lognormal'))

x = array([sizes_fit.xmin, max(team_sizes)])
y = sizes_fit.power_law.ccdf(x)
ax.plot(x,y, 'k--', label=r"$\alpha = -%.2f$""\n"r"$x_{min} = %d$"%(sizes_fit.alpha, sizes_fit.xmin))
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles[::-1], labels[::-1], loc=3)

#########
ax = fig.add_subplot(133)
x,y = num_children_fit.ccdf(original_data=True)
ax.scatter(x,y, s=s)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("Number of Recruits per Participant")
yl = ax.set_ylabel(u"p(X \u2265 x)")
ylim(1.0/10**3,1)
xlim(1, 10.0**3)
ax.annotate("C", (0,1.), xycoords=(yl, "axes fraction"), 
             fontproperties=panel_label_font) 

print(num_children_fit.alpha)
print(num_children_fit.xmin)
print(num_children_fit.loglikelihood_ratio('power_law', 'exponential'))
print(num_children_fit.loglikelihood_ratio('power_law', 'lognormal'))

x = array([sizes_fit.xmin, max(number_of_children)])
y = sizes_fit.power_law.ccdf(x)
ax.plot(x,y, 'k--', label=r"$\alpha = -%.2f$""\n"r"$x_{min} = %d$"%(num_children_fit.alpha, num_children_fit.xmin))
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles[::-1], labels[::-1], loc=3)

subplots_adjust(wspace=.3)
#suptitle("Figure S%i"%sfn)
sfn+=1
figures.append(fig)

# <markdowncell>

# Run Cox model
# ---------

# <codecell>

%load_ext rmagic

# <codecell>

%%R -o factor_labels -d model_data

mydata = read.csv("Langley_Recruits_anonymized_data.csv")

mydata$Same_Heard_From_as_Recruiter <- factor(mydata$Same_Heard_From_as_Recruiter, levels=0:2)
mydata$Same_Heard_From_as_Recruiter <- relevel(mydata$Same_Heard_From_as_Recruiter, ref="2")

mydata$Heard_From <- factor(mydata$Heard_From, levels=c(0:5,100))
mydata$Heard_From <- relevel(mydata$Heard_From, ref="0")

mydata$Age <- relevel(mydata$Age, ref="unknown")
mydata$Recruiter_Age <- relevel(mydata$Recruiter_Age, ref="unknown")

mydata$Gender <- relevel(mydata$Gender, ref="unknown")
mydata$Recruiter_Gender <- relevel(mydata$Recruiter_Gender, ref="unknown")

mydata$Location_Comparison <- relevel(mydata$Location_Comparison, ref="unknown")

library(survival)
library(rmeta)
library(car)
analysis<-coxph(Surv(Registration_Interval_Days) ~
    (Recruiter_Gender*Gender)
    + (Recruiter_Age*Age)
    + Location_Comparison
    + Heard_From
    + Same_Heard_From_as_Recruiter
    + Recruiter_Number_of_Recruits-1
    + Number_of_Recruits
    + Recruitment_Generation-1
    + Recruiter_Join_Date_Numeric_Days,
    , data=mydata
    , singular.ok=TRUE)

print(analysis$call)

q<-summary(analysis)
model_data = data.frame(coef=q$coefficients[,1], expcoef=q$conf.int[,1], lower95=q$conf.int[,3], upper95=q$conf.int[,4], se=q$coefficients[,3])
factor_labels = rownames(model_data)

ind = which(!is.na(analysis$coefficients))
V = vcov(analysis)
V = V[ind, ind]

# <markdowncell>

# Define forest plot functions
# ------

# <codecell>

def boxplot(middle, boxtop, boxbottom, whiskertop, whiskerbottom, label=None, color='Spectral_r', width=.5, spacing=1, ax=None, orientation='forest'):
    n = len(middle)
    
    middle = ma.masked_invalid(middle)
    whiskertop = ma.masked_invalid(whiskertop)
    whiskerbottom = ma.masked_invalid(whiskerbottom)
    
    positions = range(1,spacing*n+1, spacing)
    
    width = width
    width = width/2
    
    if ax==None:
        fig = figure()
        ax = fig.add_subplot(111)
    
    from matplotlib.patches import Rectangle
    from matplotlib import colors, cm
    norm = colors.LogNorm(middle.min(), middle.max())
    cmap = cm.get_cmap(color)
    
    for i in range(n):
        m = middle[i]
        if m == ma.masked:
            print("Skipping invalid value %i"%i)
            continue
        bt = boxtop[i]
        bb = boxbottom[i]
        wt = whiskertop[i]
        wb = whiskerbottom[i]
        
        if orientation=='forest':
            position = positions[-(i+1)]

            p = Rectangle((bb, position-width),bt-bb, width*2, color=cmap(norm(m)), alpha=.6)
            ax.add_patch(p)
            
            linex = [position-width, position+width]
            liney = [m, m]
            ax.plot(liney, linex, linewidth=3, color=cmap(norm(m)), alpha=1)
            
            whiskerx = [position, position, position-width, position+width]
            
            upperwhiskery = [bt, wt, wt, wt]
            ax.plot(upperwhiskery, whiskerx,  color=cmap(norm(m)))
            
            lowerwhiskery = [bb, wb, wb, wb]
            ax.plot(lowerwhiskery, whiskerx, color=cmap(norm(m)))
        else:
            position = positions[i]

            p = Rectangle((position-width, bb),width*2, bt-bb, color=cmap(norm(m)), alpha=.6)
            ax.add_patch(p)
            
            
            linex = [position-width, position+width]
            liney = [m, m]
            ax.plot(linex, liney,'k', linewidth=3, color=cmap(norm(m)), alpha=1)
            
            whiskerx = [position, position, position-width, position+width]
            
            upperwhiskery = [bt, wt, wt, wt]
            ax.plot(whiskerx, upperwhiskery, color=cmap(norm(m)))
            
            lowerwhiskery = [bb, wb, wb, wb]
            ax.plot(whiskerx, lowerwhiskery, color=cmap(norm(m)))
        
    if label:
        if orientation=='forest':
            ax.set_yticks(positions)
            ax.set_yticklabels(label[::-1])
        else:
            ax.set_xticks(positions)
            ax.set_xticklabels(label)
            
    if orientation=='forest':
        ax.set_xscale('log')
        ax.plot((1,1), ax.get_ylim(), 'k--')
        ax.set_xlabel('Hazard Ratio')
        ax.set_xlim(min(whiskerbottom)*.8, max(whiskertop)*1.2)
    else:
        ax.set_yscale('log')
        ax.plot(ax.get_xlim(), (1,1), 'k--')
        ax.set_ylabel('Hazard Ratio')
        ax.set_ylim(min(whiskerbottom)*.8, max(whiskertop)*1.2)
    return ax
    

# <codecell>

#Langleylabels = asarray(factor_labels)

#coef = model_data['coef']
#expcoef = model_data['expcoef']
#lower95 = model_data['lower95']
#upper95 = model_data['upper95']
#se = model_data['se']
#lowerse = exp(coef-se)
#upperse = exp(coef+se)

def Langleyboxplot(indices, **kwargs):
    print(factor_labels[indices])
    ax = boxplot(model_data['expcoef'][indices],
        exp(model_data['coef']+model_data['se'])[indices], exp(model_data['coef']-model_data['se'])[indices], 
        model_data['upper95'][indices], model_data['lower95'][indices],
        **kwargs)
    return ax

# <markdowncell>

# Figure 2
# ----

# <codecell>

figwidth = 3.5

fig = figure(figsize=(figwidth, figwidth/1.618))
ax = fig.add_subplot(111)
l = []
for i in ['Female', 'Male']:
    for j in ['Female', 'Male']:
        l.append(r'%s$\rightarrow$%s'%(j, i))

slice_start = 27
slice_end = 31
ax = Langleyboxplot(range(slice_start, slice_end), label=l, ax=ax)
ylabel(r'Recruiter Gender $\rightarrow$ Recruit Gender')
#ax.set_yscale('log')
#ax.annotate("A", (0,1.), xycoords=(ax.get_yaxis().get_label(), "axes fraction"), 
#             fontsize=14) 

#ax = fig.add_subplot(212)
#l = ['Parent: Female', 'Parent: Male', 'Child: Female', 'Child: Male']
#slice_start = 0
#slice_end = 4
#ax = Langleyboxplot(range(slice_start, slice_end), label=l, ax=ax)
#ax.set_yscale('log')
#ax.annotate("B", (0,1.), xycoords=(ax.get_yaxis().get_label(), "axes fraction"), 
#             fontsize=14) 




#subplots_adjust(hspace=0.5)
#suptitle("Figure %i"%fn)
#title("Figure %i"%fn)
fn+=1
figures.append(fig)

# <codecell>

%%R
hypothesis = "Recruiter_Genderfemale:Genderfemale - Recruiter_Gendermale:Gendermale"
q = linearHypothesis(analysis, hypothesis, singular.ok=TRUE, vcov.=V)
print(q)

# <markdowncell>

# Figure 3
# ----

# <codecell>

figwidth = 7.2

fig = figure(figsize=(figwidth, figwidth/1.618))
#fig = figure(figsize=(4.6,7.44295635))
#fig = figure(figsize=(4.6,2.84295635))
#fig = figure(figsize=(2.3,3.7214))
annotate_coord = (-.15, 1)

ax = fig.add_subplot(121)
l = ['Recruiter & Recruit\n Same Source', 'Recruiter & Recruit\n Different Source']
ax = Langleyboxplot([22, 21], label=l, ax=ax)


ax.set_xticks([0.5, 1, 2])
ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())

ax.annotate("A", annotate_coord, xycoords="axes fraction",
             fontproperties=panel_label_font) 


ax = fig.add_subplot(122)
l = ['Langley', 'Family', 'Friend', 'Other', 'Organization','Media']
indices = [18, 16, 15, 20, 17, 19]
ax = Langleyboxplot(indices, label=l, spacing=3, ax=ax)
ax.yaxis.tick_right()

ax.set_xticklabels([ax.get_xlim()[0], 1, 10])

ylabel('Source from which Recruit First \nHeard about the Contest')
ax.yaxis.set_label_position("right")

ax.annotate("B", annotate_coord, xycoords="axes fraction", 
             fontproperties=panel_label_font) 


#subplots_adjust(hspace=0.5)
#suptitle("Figure %i"%fn)
fn+=1
figures.append(fig)

# <codecell>

%%R -o q
hypothesis = "Same_Heard_From_as_Recruiter1 - Same_Heard_From_as_Recruiter0"
q = linearHypothesis(analysis, hypothesis, singular.ok=TRUE, vcov.=V)
print(q)

# <codecell>

%%R -o q
hypothesis = "Heard_From4 - Heard_From5"
q = linearHypothesis(analysis, hypothesis, singular.ok=TRUE, vcov.=V)
print(q)

# <markdowncell>

# Figure 4
# ----

# <codecell>

figwidth = 3.5

fig = figure(figsize=(figwidth, figwidth/1.618))

ax = fig.add_subplot(111)
l = ['Different Country', 'Different City', 'Same City']
ax = Langleyboxplot([13,12,14], label=l, ax=ax)
#ax.set_xticklabels([ax.get_xlim()[0], 1, ax.get_xlim()[1]])
ax.set_xticks([1, 2, 3])
ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())

#title("Figure %i"%fn)
fn+=1
figures.append(fig)

# <codecell>

%%R -o q
hypothesis = "Location_ComparisonDifferent Country - Location_ComparisonSame City"
q = linearHypothesis(analysis, hypothesis, singular.ok=TRUE, vcov.=V)
print(q)

# <markdowncell>

# Figure 5
# -----

# <codecell>

figwidth = 3.5

fig = figure(figsize=(7.2,7.2*1.618))

l = ["<20", "20-40", "40-60", ">60"]
fontsize=8
ax1 = fig.add_subplot(441)
        
indices = range(31,47,4)
ax1 = Langleyboxplot(indices, label=l, ax=ax1, orientation='box')
xl = xlim()
xlim(xl[0], xl[1]+.5)

ax1.set_xticklabels(l, fontsize=fontsize)
text(-.01, -.1, 'Recruit Age:', transform = ax1.transAxes, horizontalalignment='right')
text(-.01, -.25, 'Recruiter Age:', transform = ax1.transAxes, horizontalalignment='right')

group="<20"
t = ax1.get_xticks()
offset = 10**-4.5
text(mean(t[1:3]), offset, group, horizontalalignment='center')

ax1.annotate("A", (0,1.), xycoords=(ax1.get_yaxis().get_label(), "axes fraction"), 
             fontproperties=panel_label_font) 


########
ax = fig.add_subplot(442, sharey=ax1)
        
indices = range(32,47,4)
ax = Langleyboxplot(indices, ax=ax, label=l, orientation='box')
ax.set_xticklabels(l, fontsize=fontsize)

group="20-40"
t = ax.get_xticks()
offset = 10**-4.5
text(mean(t[1:3]), offset, group, horizontalalignment='center')

ax.set_ylabel("")
setp( ax.get_yticklabels(), visible=False)

########
ax = fig.add_subplot(443, sharey=ax1)
        
indices = range(33,47,4)
ax = Langleyboxplot(indices, label=l, ax=ax, orientation='box')
ax.set_xticklabels(l, fontsize=fontsize)

group="40-60"
t = ax.get_xticks()
offset = 10**-4.5
text(mean(t[1:3]), offset, group, horizontalalignment='center')

ax.set_ylabel("")
setp( ax.get_yticklabels(), visible=False)
ax.set_ylim(10**-3,10**3)

########
ax = fig.add_subplot(444)
        
indices = range(34,47,4)
ax = Langleyboxplot(indices, label=l, ax=ax, orientation='box')
ax.set_xticklabels(l, fontsize=fontsize)

group=">60"
t = ax.get_xticks()
offset = 10**-4.5
text(mean(t[1:3]), offset, group, horizontalalignment='center')


ax.set_ylabel("")
setp( ax.get_yticklabels(), visible=False)
ax.set_ylim(10**-3,10**3)

xl = xlim()
xlim(xl[0]-.5, xl[1]+.5)

#########
ax = fig.add_subplot(412)
l = ["<20", "20-40", "40-60", ">60"]
slice_start = 8
slice_end = 12
ax = Langleyboxplot(range(slice_start, slice_end), label=l, ax=ax, orientation='box')
xlabel('Recruit Age Group')
ax.set_yscale('log')
ax.annotate("B", (0,1.), xycoords=(ax.get_yaxis().get_label(), "axes fraction"), 
             fontproperties=panel_label_font) 

#########
ax1 = fig.add_subplot(4,4,9)

l = ["<20", "20-40", "40-60", ">60"]

        
indices = range(31,35)
ax1 = Langleyboxplot(indices, label=l, ax=ax1, orientation='box')
xl = xlim()
xlim(xl[0], xl[1]+.5)
ax1.set_xticklabels(l, fontsize=fontsize)

#ax1.set_xticklabels(["<20", "20-40", "40-60", ">60"], fontsize=8)
text(-.01, -.1, 'Recruiter Age:', transform = ax1.transAxes, horizontalalignment='right')
text(-.01, -.25, 'Recruit Age:', transform = ax1.transAxes, horizontalalignment='right')

group="<20"
t = ax.get_xticks()
offset = 10**-4.5
text(mean(t[1:3]), offset, group, horizontalalignment='center')

ax1.annotate("C", (0,1.), xycoords=(ax1.get_yaxis().get_label(), "axes fraction"), 
             fontproperties=panel_label_font) 


########
ax = fig.add_subplot(4,4,10, sharey=ax1)
        
indices = range(35,39)
ax = Langleyboxplot(indices, ax=ax, label=l, orientation='box')
ax.set_xticklabels(l, fontsize=fontsize)

group="20-40"
t = ax.get_xticks()
offset = 10**-4.5
text(mean(t[1:3]), offset, group, horizontalalignment='center')

ax.set_ylabel("")
setp( ax.get_yticklabels(), visible=False)

########
ax = fig.add_subplot(4,4,11, sharey=ax1)
        
indices = range(39,43)
ax = Langleyboxplot(indices, label=l, ax=ax, orientation='box')
ax.set_xticklabels(l, fontsize=fontsize)

group="40-60"
t = ax.get_xticks()
offset = 10**-4.5
text(mean(t[1:3]), offset, group, horizontalalignment='center')

ax.set_ylabel("")
setp( ax.get_yticklabels(), visible=False)
ax.set_ylim(10**-3,10**3)

########
ax = fig.add_subplot(4,4,12)
        
indices = range(43,47)
ax = Langleyboxplot(indices, label=l, ax=ax, orientation='box')
ax.set_xticklabels(l, fontsize=fontsize)

group=">60"
t = ax.get_xticks()
offset = 10**-4.5
text(mean(t[1:3]), offset, group, horizontalalignment='center')


ax.set_ylabel("")
setp( ax.get_yticklabels(), visible=False)
ax.set_ylim(10**-3,10**3)

xl = xlim()
xlim(xl[0]-.5, xl[1]+.5)


#########
ax = fig.add_subplot(414)
l = ["<20", "20-40", "40-60", ">60"]
slice_start = 4
slice_end = 8
ax = Langleyboxplot(range(slice_start, slice_end), label=l, ax=ax, orientation='box')
xlabel('Recruiter Age Group')
ax.set_yscale('log')
ax.annotate("D", (0,1.), xycoords=(ax.get_yaxis().get_label(), "axes fraction"), 
             fontproperties=panel_label_font) 

subplots_adjust(hspace=0.5)
#suptitle("Figure %i"%fn)
fn+=1
figures.append(fig)

# <codecell>

%%R -o q
hypothesis = "Age1 - Age4"
q = linearHypothesis(analysis, hypothesis, singular.ok=TRUE, vcov.=V)
print(q)

# <markdowncell>

# Supporting Information
# ----

# <markdowncell>

# Figure S1: Mobilization speed descriptive statistics
# ----

# <codecell>

%%R -o mobilization_times
mobilization_times = mydata$Registration_Interval_Days

# <codecell>

print(mean(mobilization_times))
print(median(mobilization_times))
print(std(mobilization_times))
from scipy.stats import skew
print skew(mobilization_times)

figwidth = 3.5
figsize(figwidth, figwidth/1.618)
hist(mobilization_times)
xlabel("Mobilization Speed (Days)")
ylabel("Participant Count")
figures.append(gcf())

# <codecell>

import powerlaw
fit = powerlaw.Fit(mobilization_times)
fit.plot_ccdf()
fit.power_law.plot_ccdf()
fit.exponential.plot_ccdf()
fit.lognormal.plot_ccdf()
print fit.distribution_compare('lognormal', 'exponential')

figure()
fit = powerlaw.Fit(mobilization_times, xmin=1)
fit.plot_ccdf()
fit.power_law.plot_ccdf()
fit.exponential.plot_ccdf()
fit.lognormal.plot_ccdf()
print fit.distribution_compare('lognormal', 'exponential')

# <markdowncell>

# SI: Model Checking
# ----

# <codecell>

%%R
print(summary(analysis))

# <codecell>

%%R
pdf('Model_Fit_Supporting_Information.pdf', paper="a4", height=9)
par(mfrow = c(4,3))
zph<-cox.zph(analysis)
target_variables<-which(
    ( 
    #All the target variables are either an interaction or one of the "Heard_From" factors.
    grepl(":", rownames(zph$table)) | 
    grepl("Heard_From", rownames(zph$table))
    ) &
    !is.na(zph$table[,1])
    )
plot(zph[target_variables])

# <markdowncell>

# Figure S2: Other Control Variables
# ----

# <codecell>

figwidth = 3.5

fig = plt.figure(figsize=(figwidth, figwidth/1.618))

ax = fig.add_subplot(111)
l = ['Additional Day after\nRegistration Opened\n(Inverse of Days Left Until Contest)', 
     'Additional Generation\nin Team after the First',
    "Recruit Recruiting an\n Additional Future Recruit"]

slice_start = 24
slice_end = 27
ax = Langleyboxplot([26, 25,24], label=l, ax=ax, orientation='forest')
#ax.set_yticks([0.5, 1, 2])
#ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
#ax.xaxis.label.set_size(5)
ax.set_xticks([0.5, 1, 2])
ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
ax.yaxis.label.set_size(7)



#ax.annotate("B", (0,1.), xycoords=(ax.get_yaxis().get_label(), "axes fraction"), 
#             fontsize=14) 

#suptitle("Figure S%i"%sfn)
figures.append(fig)

# <codecell>

##Principles taken from http://matplotlib.1069221.n5.nabble.com/svg-in-plot-td27904.html
#fig.savefig("ChildrenandTime.eps")
#
#from pyx import canvas, epsfile 
#
#c = canvas.canvas() 
## load both external files 
#c.insert(epsfile.epsfile(0, 0, "ChildrenandTime.eps")) 
#c.insert(epsfile.epsfile(4, 17, "Parent-nChild-Diagram1.eps", scale=1.4)) 
#c.insert(epsfile.epsfile(13.5, 17, "Parent-nChild-Diagram2.eps", scale=1.4)) 
#
## save generated EPS files 
#c.writeEPSfile("FigureS3") 
#
#sfn+=1

# <codecell>

#import matplotlib.image as mpimg
#img=mpimg.imread('/data/alstottjd/Langley/Payout_diagram.png')
#
#fig = plt.figure()
#imgplot = plt.imshow(img)
#imgplot.axes.get_xaxis().set_visible(False)
#imgplot.axes.get_yaxis().set_visible(False)
#imgplot.axes.set_frame_on(False)
#
##title("Figure S%i"%sfn)
#sfn+=1
##figures.append(fig)

# <codecell>

from matplotlib.backends.backend_pdf import PdfPages
plots = PdfPages('Figures.pdf')
for i in figures:
    print i
    plots.savefig(i, bbox_inches='tight')
plots.close()

