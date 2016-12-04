from __future__ import division

import matplotlib
matplotlib.use('TkAgg')

from pylab import *
import networkx as nx

path = 11.0
selfinfluece = 0        # use self-influence?
treatdataset = 0        # treat dataset?

meanvalues = []

### simulation parameters
def Path (val = path):
    global path
    path = str(val)
    return val

def SelfInfluence (val = selfinfluece):
    global selfinfluece
    selfinfluece = int(val)
    return val

def TreatDataset (val = treatdataset):
    global treatdataset
    treatdataset = int(val)
    return val


### simulation steps
def initialize():
    global g, nextg, r, path, treatdataset, selfinfluece, meanvalues

    # read graph from .gml file
    g = nx.read_gml('./data/' + path + '.gml')

    # TreatDataset == 1 ...
    #   remove nodes with no edge
    #   set value 0 to -1.
    #   set value 1 to  1.
    if (treatdataset):
        zeros = []
        for i in g.nodes_iter():
            if (g.node[i]['value'] == 0):
                g.node[i]['value'] = -1.
            else:
                g.node[i]['value'] =  1.

            if (g.degree(i) == 0):
                zeros.append(i)

        for i in zeros:
            g.remove_node(i)

    # set graph layout
    g.pos = nx.spring_layout(g)

    # get reverse graph
    r = g.reverse()

    # calculate network mean value
    acc = 0
    meanvalues = []
    for i in g.nodes_iter():
        acc += g.node[i]['value']

    meanvalues.append(acc / g.order())

    nextg = g.copy()


def observe():
    global g, nextg, meanvalues

    ## plot network
    figure(1)
    cla()                           # clear plot

    axis('off')                     # remove axis
    gcf().set_facecolor('white')    # set background to white
    gcf().tight_layout()            # remove white space

    # draw nodes
    nodes = nx.draw_networkx_nodes(g, cmap = cm.coolwarm, vmin = -1, vmax = 1,
        node_color = [g.node[i]['value'] for i in g.nodes_iter()],
        node_size = 50, pos = g.pos)
    nodes.set_edgecolor('None')     # remove node border

    # draw edges
    nx.draw_networkx_edges(g, pos = g.pos, alpha = 0.1)


    ## plot histogram
    figure(2)
    cla()                           # clear plot

    # get histdata
    hitsdata = []
    for i in g.nodes_iter():
        hitsdata.append(g.node[i]['value'])

    # get wieghts to normilize histdata
    weights = np.ones_like(hitsdata)/len(hitsdata)

    # plot histdata
    hist(hitsdata, bins = linspace(-1.2, 1.2, 125), weights = weights,
        linewidth = 0.25, color = '0.75')

    # plot vertical line at meanvalue
    if (len(meanvalues) > 0):
        plot((meanvalues[-1], meanvalues[-1]), (0, 0.05), 'r-', alpha = 0.4, linewidth = 4)

    # set histogram plot limits
    xlim([-1.2,1.2])


def update():
    global g, nextg, r, selfinfluece, meanvalues

    acc = 0
    for i in g.nodes_iter():
        ic   = 0
        nc   = 0

        # calculate selfinfluece
        if (selfinfluece):
            value = g.node[i]['value']
            links = len(r.out_edges(i))         # get edges from i to any j
            ic = value * links                  # influence
            nc = links                          # links' count

        # calculate neighborhood influence
        for j in g.neighbors(i):
            value = g.node[j]['value']
            links = len(r.out_edges(j))         # get edges from j to any k
            ic += value * links                 # influence
            nc += links                         # links' count

        # update node value
        if (nc != 0):
            nextg.node[i]['value'] = ic / nc

    # get network mean value
    for i in nextg.nodes_iter():
        acc += nextg.node[i]['value']
        meanvalues.append(acc / g.order())

    # update networks
    g, nextg = nextg, g


## call for PyCX
import pycxsimulator
pycxsimulator.GUI(parameterSetters = [Path, TreatDataset, SelfInfluence]).start(
    func=[initialize, observe, update])
