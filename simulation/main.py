import matplotlib
matplotlib.use('TkAgg')

from pylab import *
import networkx as nx

path = 101.0
si   = 0
td   = 0

def Path (val = path):
    global path
    path = str(val)
    return val

def SelfInfluence (val = si):
    global si
    si = int(val)
    return val

def TreatDataset (val = td):
    global td
    td = int(val)
    return val

def initialize():
    global g, nextg, path, si
    g = nx.read_gml('./data/' + path + '.gml')
    g.pos = nx.spring_layout(g)

    if (td):
        zeros = []
        for i in g.nodes_iter():
            if (g.node[i]['value'] == 0):
                g.node[i]['value'] = -1.0
            else:
                g.node[i]['value'] = 1.0

            if (g.degree(i) == 0):
                zeros.append(i)

        for i in zeros:
            g.remove_node(i)

    nextg = g.copy()

def observe():
    global g, nextg
    cla()
    axis('off')
    gcf().set_facecolor('white')
    gcf().tight_layout()

    nodes = nx.draw_networkx_nodes(g, cmap = cm.coolwarm, vmin = -1, vmax = 1,
                node_color = [g.node[i]['value'] for i in g.nodes_iter()],
                node_size = 50, pos = g.pos)
    nodes.set_edgecolor('None')
    nx.draw_networkx_edges(g, pos = g.pos, alpha = 0.1)

def update():
    global g, nextg
    for i in g.nodes_iter():

        if (si):
            value = g.node[i]['value']
            links = g.degree(i)
            ic = value * links                  # influence count
            nc = links                          # n count

        else:
            ic = 0
            nc = 0

        for j in g.neighbors(i):
            value = g.node[j]['value']
            links = g.degree(i)
            ic += value * links
            nc += links

        if (nc != 0):
            nextg.node[i]['value'] = ic / nc

    g, nextg = nextg, g

import pycxsimulator
pycxsimulator.GUI(parameterSetters = [Path, SelfInfluence, TreatDataset]).start(
    func=[initialize, observe, update])
