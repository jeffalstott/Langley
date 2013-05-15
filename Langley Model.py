# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

%load_ext rmagic

# <codecell>

cd /data/alstottjd/Langley/

# <codecell>

figures = []
fn = 1
sfn = 1

# <codecell>

coef = []
expcoef = []
lower95 = []
upper95 = []
se = []

import csv
with open('analysis.csv') as csvfile:
    analysisreader = csv.reader(csvfile)
    labels = []

    for row in analysisreader:
        print(row)
        if row[0]=="":
            continue
        
        labels.append(row[0])
        
        for j in range(1,len(row)):
            try:
                row[j]=float(row[j])
            except:
                row[j] = nan
            
            if row[j] == 0:
                row[j] = nan
        
        coef.append(row[1])
        expcoef.append(row[2])
        lower95.append(row[3])
        upper95.append(row[4])
        se.append(row[5])

# <codecell>

coef = asarray(coef)
expcoef = asarray(expcoef)
lower95 = asarray(lower95)
upper95 = asarray(upper95)
se = asarray(se)
Langleylabels = asarray(labels)

# <codecell>

lowerse = exp(coef-se)
upperse = exp(coef+se)

# <codecell>

def boxplot(middle, boxtop, boxbottom, whiskertop, whiskerbottom, label=None, width=.5, spacing=1, ax=None):
    n = len(middle)
    positions = range(1,spacing*n+1, spacing)
    
    width = width
    width = width/2
    
    if ax==None:
        fig = figure()
        ax = fig.add_subplot(111)
    
    for i in range(n):
        position = positions[i]
        m = middle[i]
        bt = boxtop[i]
        bb = boxbottom[i]
        wt = whiskertop[i]
        wb = whiskerbottom[i]
        
        boxx = [position-width, position-width, position+width, position+width, position-width]
        boxy = [bb, bt, bt, bb, bb]
        ax.plot(boxx, boxy, 'k', linewidth=2)
        
        linex = [position-width, position+width]
        liney = [m, m]
        ax.plot(linex, liney,'k', linewidth=4)
        
        whiskerx = [position, position, position-width, position+width]
        
        upperwhiskery = [bt, wt, wt, wt]
        ax.plot(whiskerx, upperwhiskery, 'k')
        
        lowerwhiskery = [bb, wb, wb, wb]
        ax.plot(whiskerx, lowerwhiskery, 'k')
        
    if label:
        ax.set_xticks(positions)
        ax.set_xticklabels(label)
            
    return ax
    

# <codecell>

def Langleyboxplot(indices, **kwargs):
    print(Langleylabels[indices])
    ax = boxplot(expcoef[indices], 
        upperse[indices], lowerse[indices], 
        upper95[indices], lower95[indices], 
        **kwargs)
    ax.plot(xlim(), (1,1), 'k--')
    ylabel('Hazard Ratio')
    
    return ax

# <codecell>

%%R
source('/home/alstottjd/Code/Langley/analysis_script.r')
library(car)
ind = which(!is.na(analysis$coefficients))
V = vcov(analysis)
V = V[ind, ind]

# <codecell>

fig = figure()
#fig = figure(figsize=(4.6,7.44295635))
#fig = figure(figsize=(4.6,2.84295635))
#fig = figure(figsize=(2.3,3.7214))

ax = fig.add_subplot(211)
#l = ['Friend', 'Family', 'Organization', 'Langley', 'Media', 'Other']
#slice_start = 14
#slice_end = 20
l = ['Langley', 'Family', 'Friend', 'Other', 'Organization','Media']
indices = [17, 15, 14, 19, 16 , 18]
ax = Langleyboxplot(indices, label=l, spacing=3, ax=ax)
ax.set_yscale('log')
xlabel('Source from which Child Heard about the Contest')
ax.annotate("A", (0,1.), xycoords=(ax.get_yaxis().get_label(), "axes fraction"), 
             fontsize=14) 

ax = fig.add_subplot(212)
l = ['Parent & Child\n Same Source', 'Parent & Child\n Different Source']
slice_start = 12
slice_end = 14
ax = Langleyboxplot(range(slice_start, slice_end), label=l, ax=ax)
ax.annotate("B", (0,1.), xycoords=(ax.get_yaxis().get_label(), "axes fraction"), 
             fontsize=14) 


subplots_adjust(hspace=0.5)
#suptitle("Figure %i"%fn)
fn+=1
figures.append(fig)

# <codecell>

%%R -o q
hypothesis = "Relationship_with_Parent4 - Relationship_with_Parent5"
q = linearHypothesis(analysis, hypothesis, singular.ok=TRUE, vcov.=V)
print(q)

# <codecell>

fig = figure()
ax = fig.add_subplot(111)
l = ['Different Country', 'Different City', 'Same City']
slice_start = 20
slice_end = 23
ax = Langleyboxplot(range(slice_start, slice_end), label=l, ax=ax)

#title("Figure %i"%fn)
fn+=1
figures.append(fig)

# <codecell>

%%R -o q
hypothesis = "Parent_Child_LocationDifferent Country - Parent_Child_LocationSame City"
q = linearHypothesis(analysis, hypothesis, singular.ok=TRUE, vcov.=V)
print(q)

# <codecell>

fig = figure()

ax = fig.add_subplot(111)
l = []
for i in ['Female', 'Male']:
    for j in ['Female', 'Male']:
        l.append(r'%s$\rightarrow$%s'%(j, i))

slice_start = 27
slice_end = 31
ax = Langleyboxplot(range(slice_start, slice_end), label=l, ax=ax)
xlabel(r'Parent Gender $\rightarrow$ Child Gender')
ax.set_yscale('log')
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
hypothesis = "Parent_Genderfemale:Genderfemale - Parent_Gendermale:Gendermale"
q = linearHypothesis(analysis, hypothesis, singular.ok=TRUE, vcov.=V)
print(q)

# <codecell>

fig = figure(figsize=(8.5, 11))


ax = fig.add_subplot(411)
l = []
for i in range(1,5):
    for j in range(1,5):
        l.append(r'%i$\rightarrow$%i'%(i, j))
        
indices = []
indices = indices + range(31,47,4)
indices = indices + range(32,47,4)
indices = indices + range(33,47,4)
indices = indices + range(34,47,4)

ax = Langleyboxplot(indices, label=l, ax=ax)
ax.set_yscale('log')
xl = xlim()
xlim(xl[0], xl[1]+1)

ax.annotate("A", (0,1.), xycoords=(ax.get_yaxis().get_label(), "axes fraction"), 
             fontsize=14) 

ax.set_xticklabels(["<20", "20-40", "40-60", ">60", "<20", "20-40", "40-60", ">60", "<20", "20-40", "40-60", ">60", "<20", "20-40", "40-60", ">60"], fontsize=8)
text(-.01, -.1, 'Child Age:', transform = ax.transAxes, horizontalalignment='right')
text(-.01, -.25, 'Parent Age:', transform = ax.transAxes, horizontalalignment='right')
t = ax.get_xticks()
offset = 10**-4.5
text(mean(t[1:3]), offset, "<20", horizontalalignment='center')
text(mean(t[5:7]), offset, "20-40", horizontalalignment='center')
text(mean(t[9:11]), offset, "40-60", horizontalalignment='center')
text(mean(t[12:15]), offset, ">60", horizontalalignment='center')



ax = fig.add_subplot(412)
l = ["<20", "20-40", "40-60", ">60"]
slice_start = 8
slice_end = 12
ax = Langleyboxplot(range(slice_start, slice_end), label=l, ax=ax)
xlabel('Child Age Group')
ax.set_yscale('log')
ax.annotate("B", (0,1.), xycoords=(ax.get_yaxis().get_label(), "axes fraction"), 
             fontsize=14) 


ax = fig.add_subplot(413)
l = []
for i in range(1,5):
    for j in range(1,5):
        l.append(r'%i$\rightarrow$%i'%(j, i))
        
slice_start = 31
slice_end = 47
ax = Langleyboxplot(range(slice_start, slice_end), label=l, ax=ax)
ax.set_yscale('log')
xl = xlim()
xlim(xl[0], xl[1]+1)
#xlabel(r'Parent Age Group $\rightarrow$ Child Age Group (Grouped by Child Age)')
ax.annotate("C", (0,1.), xycoords=(ax.get_yaxis().get_label(), "axes fraction"), 
             fontsize=14) 


ax.set_xticklabels(["<20", "20-40", "40-60", ">60", "<20", "20-40", "40-60", ">60", "<20", "20-40", "40-60", ">60", "<20", "20-40", "40-60", ">60"], fontsize=8)
text(-.01, -.1, 'Parent Age:', transform = ax.transAxes, horizontalalignment='right')
text(-.01, -.25, 'Child Age:', transform = ax.transAxes, horizontalalignment='right')
t = ax.get_xticks()
offset = 10**-4.5
text(mean(t[1:3]), offset, "<20", horizontalalignment='center')
text(mean(t[5:7]), offset, "20-40", horizontalalignment='center')
text(mean(t[9:11]), offset, "40-60", horizontalalignment='center')
text(mean(t[12:15]), offset, ">60", horizontalalignment='center')

ax = fig.add_subplot(414)
l = ["<20", "20-40", "40-60", ">60"]
slice_start = 4
slice_end = 8
ax = Langleyboxplot(range(slice_start, slice_end), label=l, ax=ax)
xlabel('Parent Age Group')
ax.set_yscale('log')
ax.annotate("D", (0,1.), xycoords=(ax.get_yaxis().get_label(), "axes fraction"), 
             fontsize=14) 

subplots_adjust(hspace=0.5)
#suptitle("Figure %i"%fn)
fn+=1
figures.append(fig)

# <codecell>

%%R -o q
hypothesis = "Age1 - Age4"
q = linearHypothesis(analysis, hypothesis, singular.ok=TRUE, vcov.=V)
print(q)

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

# <codecell>

import matplotlib.cm as cm

fig = figure(figsize=(12,8))
i = 3 #Picked team number 3
d = max_depth(C[i])
#title("Example team, %i members, %.0f generations"%(len(C[i].node), d))
pos=networkx.spring_layout(C[i].to_undirected())
#pos=networkx.graphviz_layout(C[i],prog="twopi",root=0)
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
fig.add_subplot(111)
networkx.draw(C[i],pos,node_size=node_size,
    alpha=alpha, width=width, 
    with_labels=False, 
    node_color = depth_colors, edge_color = same_relationship_colors, 
    arrows=True)

#networkx.draw_networkx_nodes(C[i],pos,nodelist=[926],node_shape='s', node_color='k', node_size=100)


#annotate("A", (0,1.), xycoords="axes fraction", 
#             fontsize=14) 
#S1.add_subplot(312)
#networkx.draw(C[i],pos,node_size=node_size,alpha=alpha, width=width, with_labels=False, node_color = depth_colors, edge_color = same_media_colors)
#annotate("B", (0,1.), xycoords= "axes fraction", 
#             fontsize=14) 
#S1.add_subplot(313)
#networkx.draw(C[i],pos,node_size=node_size,alpha=alpha, width = width, with_labels=False, node_color = depth_colors, edge_color = same_relationship_colors)
#annotate("C", (0,1.), xycoords= "axes fraction", 
#             fontsize=14) 

#title("Figure S%i"%sfn)
sfn+=1
figures.append(fig)

# <codecell>

import matplotlib.image as mpimg
img=mpimg.imread('/data/alstottjd/Langley/Payout_diagram.png')

fig = plt.figure()
imgplot = plt.imshow(img)
imgplot.axes.get_xaxis().set_visible(False)
imgplot.axes.get_yaxis().set_visible(False)
imgplot.axes.set_frame_on(False)

#title("Figure S%i"%sfn)
sfn+=1
figures.append(fig)

# <codecell>

fig = figure(figsize=(8.5, 11))
ax = fig.add_subplot(211)
l = ["Parent's Number\n of Children", "Child's Number\n of Future Children"]
slice_start = 23
slice_end = 25
ax = Langleyboxplot(range(slice_start, slice_end), label=l, ax=ax)
ax.annotate("A", (0,1.), xycoords=(ax.get_yaxis().get_label(), "axes fraction"), 
             fontsize=14) 

ax = fig.add_subplot(212)
l = [ 'Additional Generation\nin Team after the First', 'Additional Day after Registration Opened\n(Inverse of Days Left Until Contest)']
slice_start = 25
slice_end = 27
ax = Langleyboxplot(range(slice_start, slice_end), label=l, ax=ax)
ax.annotate("B", (0,1.), xycoords=(ax.get_yaxis().get_label(), "axes fraction"), 
             fontsize=14) 

#suptitle("Figure S%i"%sfn)
figures.append(fig)

# <codecell>

#Principles taken from http://matplotlib.1069221.n5.nabble.com/svg-in-plot-td27904.html
fig.savefig("ChildrenandTime.eps")

from pyx import canvas, epsfile 

c = canvas.canvas() 
# load both external files 
c.insert(epsfile.epsfile(0, 0, "ChildrenandTime.eps")) 
c.insert(epsfile.epsfile(4, 17, "Parent-nChild-Diagram1.eps", scale=1.4)) 
c.insert(epsfile.epsfile(13.5, 17, "Parent-nChild-Diagram2.eps", scale=1.4)) 

# save generated EPS files 
c.writeEPSfile("FigureS3") 

sfn+=1

# <codecell>

import powerlaw

#generations = numpy.array(networkx.get_node_attributes(G, 'depth').values())
#generations = generations[generations>0]
#generations_fit = powerlaw.Fit(generations, discrete=True)

depth = numpy.zeros(len(C))
for i in range(len(C)):
    generations = numpy.array(networkx.get_node_attributes(C[i], 'depth').values())
    depth[i] = max(generations)
depth = depth[depth>0]
depth_fit = powerlaw.Fit(depth, discrete=True)

team_sizes = numpy.zeros(len(C))
for i in range(len(C)):
    team_sizes[i] = networkx.number_of_nodes(C[i])
sizes_fit = powerlaw.Fit(team_sizes, discrete=True)

number_of_children = asarray(G.out_degree().values())
number_of_children = number_of_children[number_of_children>0]
num_children_fit = powerlaw.Fit(number_of_children, discrete=True)

s = 50
fig = plt.figure(figsize=(12,4))
ax = fig.add_subplot(131)
x,y = depth_fit.ccdf(original_data=True)
ax.scatter(x,y, s=s)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("x (Team Generations)")
yl = ax.set_ylabel(u"p(X \u2265 x)")
xlim(1,10)
ylim(10**-3,1)
ax.annotate("A", (0,1.), xycoords=(yl, "axes fraction"), 
             fontsize=14) 

print(depth_fit.alpha)
print(depth_fit.xmin)
print(depth_fit.loglikelihood_ratio('power_law', 'exponential'))
print(depth_fit.loglikelihood_ratio('power_law', 'lognormal'))

fit_start = where(x==depth_fit.xmin)[0][0]
y = depth_fit.power_law.ccdf(None)
ax.plot(x[fit_start:],y, 'k--', label=r"$\alpha = -%.2f$""\n"r"$x_{min} = %d$"%(depth_fit.alpha, depth_fit.xmin))
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles[::-1], labels[::-1], loc=3)

ax = fig.add_subplot(132)
x,y = sizes_fit.ccdf(original_data=True)
ax.scatter(x,y, s=s)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("x (Team Size)")
yl = ax.set_ylabel(u"p(X \u2265 x)")
ylim(10**-3,1)
xlim(1, 10**3)
ax.annotate("B", (0,1.), xycoords=(yl, "axes fraction"), 
             fontsize=14) 

print(sizes_fit.alpha)
print(sizes_fit.xmin)
print(sizes_fit.loglikelihood_ratio('power_law', 'exponential'))
print(sizes_fit.loglikelihood_ratio('power_law', 'lognormal'))

fit_start = where(x==sizes_fit.xmin)[0][0]
y = sizes_fit.power_law.ccdf(None)
ax.plot(x[fit_start:],y, 'k--', label=r"$\alpha = -%.2f$""\n"r"$x_{min} = %d$"%(sizes_fit.alpha, sizes_fit.xmin))
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles[::-1], labels[::-1], loc=3)

ax = fig.add_subplot(133)
x,y = num_children_fit.ccdf(original_data=True)
ax.scatter(x,y, s=s)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("x (Number of Children)")
yl = ax.set_ylabel(u"p(X \u2265 x)")
ylim(1.0/10**3,1)
xlim(1, 10.0**3)
ax.annotate("C", (0,1.), xycoords=(yl, "axes fraction"), 
             fontsize=14) 

print(num_children_fit.alpha)
print(num_children_fit.xmin)
print(num_children_fit.loglikelihood_ratio('power_law', 'exponential'))
print(num_children_fit.loglikelihood_ratio('power_law', 'lognormal'))

fit_start = where(x==num_children_fit.xmin)[0][0]
y = num_children_fit.power_law.ccdf(None)
ax.plot(x[fit_start:],y, 'k--', label=r"$\alpha = -%.2f$""\n"r"$x_{min} = %d$"%(num_children_fit.alpha, num_children_fit.xmin))
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles[::-1], labels[::-1], loc=3)

subplots_adjust(wspace=0.3)
#suptitle("Figure S%i"%sfn)
sfn+=1
figures.append(fig)

# <codecell>

from matplotlib.backends.backend_pdf import PdfPages
plots = PdfPages('Figures.pdf')
for i in figures:
    print i
    plots.savefig(i)
plots.close()

