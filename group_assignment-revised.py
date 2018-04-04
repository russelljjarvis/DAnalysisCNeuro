import pyNN.neuron as sim
nproc = sim.num_processes()
node = sim.rank()

print(nproc)
import matplotlib
matplotlib.use('Agg')
import mpi4py

threads  = sim.rank()
rngseed  = 98765
parallel_safe = True
extra = {'threads' : threads}

import matplotlib.pyplot as plt

import os
import pandas as pd
import sys
import matplotlib as mpl

import numpy as np
from pyNN.neuron import STDPMechanism
import copy
from pyNN.random import RandomDistribution, NumpyRNG
import pyNN.neuron as neuron
from pyNN.neuron import h
from pyNN.neuron import StandardCellType, ParameterSpace
from pyNN.random import RandomDistribution, NumpyRNG
from pyNN.neuron import STDPMechanism, SpikePairRule, AdditiveWeightDependence, FromListConnector, TsodyksMarkramSynapse
from pyNN.neuron import Projection, OneToOneConnector
from numpy import arange
import pyNN
from pyNN.utility import get_simulator, init_logging, normalized_filename
import random
import socket
from neuronunit.optimization import get_neab
import networkx as nx
#os.system('pip install graph_tool')

sim = pyNN.neuron

#get_ipython().magic('matplotlib inline')
mpl.rcParams.update({'font.size':16})
installs = ['bbp_client','neuron','mpi4py','xlrd','pyNN','seaborn','lazyarray','neo','neuron','brian2']
def install_deps(i):
  '''
  Hack in dependencies into to sys.path
  '''
  import os
  if i not in sys.path:
    os.system('pip install '+str(i))
'''
System admin:
_ = list(map(install_deps,installs))
import os
#Compile NEUORN mod files.
temp = os.getcwd()
os.chdir('/opt/conda/lib/python3.5/site-packages/pyNN/neuron/nmodl')
get_ipython().system('nrnivmodl')
os.chdir(temp)
# Get some hippocampus connectivity data, based on a conversation with
# academic researchers on GH:
# https://github.com/Hippocampome-Org/GraphTheory/issues?q=is%3Aissue+is%3Aclosed
# scrape hippocamome connectivity data, that I intend to use to program neuromorphic hardware.
# conditionally get files if they don't exist.
'''

path_xl = '_hybrid_connectivity_matrix_20171103_092033.xlsx'
if not os.path.exists(path_xl):
    os.system('wget https://github.com/Hippocampome-Org/GraphTheory/files/1657258/_hybrid_connectivity_matrix_20171103_092033.xlsx')

xl = pd.ExcelFile(path_xl)
dfEE = xl.parse()
dfEE.loc[0].keys()
dfm = dfEE.as_matrix()
filtered = dfm[:,3:]
filtered = filtered[1:]
EElist = []
IIlist = []

rng = NumpyRNG(seed=64754)
delay_distr = RandomDistribution('normal', [35, 1e-3], rng=rng)



for i,j in enumerate(filtered):
  # IIlist = list(filter(lambda x: x == 1 or x==2 , j))

  for k,xaxis in enumerate(j):
    if xaxis==1 or xaxis ==2:
      source = i
      target = k
      delay = delay_distr.next()
      weight = 11.0
      EElist.append((source,target,delay,weight))

    if xaxis==-1 or xaxis ==-2:
      source = i
      target = k
      delay = delay_distr.next()
      weight = 11.0
      IIlist.append((source,target,delay,weight))

import matplotlib
matplotlib.pyplot.imshow
ml = len(filtered[1])+1
plot_excit = np.zeros(shape=(ml,ml), dtype=bool)
plot_inhib = np.zeros(shape=(ml,ml), dtype=bool)
pre_exc = []
post_exc = []
pre_inh = []
post_inh = []

for i in EElist:
    plot_excit[i[0],i[1]] = int(0)
    if i[0]!=i[1]:
        plot_excit[i[0],i[1]] = int(1)
        pre_exc.append(i[0])
        post_exc.append(i[1])


assert len(pre_exc) == len(post_exc)
for i in IIlist:
    plot_inhib[i[0],i[1]] = 0
    if i[0]!=i[1]:
        plot_inhib[i[0],i[1]] = 1
        pre_inh.append(i[0])
        post_inh.append(i[1])
assert len(pre_inh) == len(post_inh)


#from graph_tool.all import motif_significance, load_graph_from_csv
#bc = load_graph_from_csv('blogcatalog.edges', directed=False, csv_options={'quotechar': '"', 'delimiter': ' '})



import pickle
with open('connections.p','wb') as f:
   pickle.dump([post_inh,pre_inh,pre_exc,post_exc],f)

index_exc = [ i for i,d in enumerate(dfm) if '+' in d[0] ]
index_inh = [ i for i,d in enumerate(dfm) if '-' in d[0] ]

# # Plot all the Projection pairs as a connection matrix (Excitatory and Inhibitory Connections)

#sns.pairplot(df, hue="species")
from scipy.sparse import coo_matrix
m = np.matrix(filtered[1:])

bool_matrix = np.add(plot_excit,plot_inhib)
with open('bool_matrix.p','wb') as f:
   pickle.dump(bool_matrix,f)

if not isinstance(m, coo_matrix):
    m = coo_matrix(m)


G = nx.DiGraph(m)
#https://git.skewed.de/count0/graph-tool/issues/366
#m, z = motif_significance(G, k=4, n_shuffles=10)
#small_world_grid = nx.navigable_small_world_graph(ml)#, p=1, q=1, r=2, dim=2, seed=None)
#small_world_ring = nx.watts_strogatz_graph(ml)

fig = matplotlib.pyplot.figure()
ax = fig.add_subplot(111, axisbg='black')
ax.plot(m.col, m.row, 's', color='white', ms=1)
ax.set_xlim(0, m.shape[1])
ax.set_ylim(0, m.shape[0])
ax.set_aspect('equal')
for spine in ax.spines.values():
    spine.set_visible(False)
ax.invert_yaxis()
ax.set_aspect('equal')
ax.set_xticks([])
ax.set_yticks([])
#fig.savefig('blah.png')
#ax.figure.show()

# # A plot of the excitatory synapse connectivity matrix
#
#matplotlib.pyplot.imshow(plot_excit)
# # A plot of the inhibitory synapse connectivity matrix
#
#matplotlib.pyplot.imshow(plot_inhib)
assert len(set(pre_exc)) < len(pre_exc)
print(len(set(pre_exc)),len(pre_exc))

#sim.setup(timestep=0.001, min_delay=1.0, **extra)

nproc = sim.num_processes()
host_name = socket.gethostname()
node_id = sim.setup(timestep=0.01, min_delay=1.0, **extra)
print("Host #%d is on %s" % (node_id + 1, host_name))
print("%s Initialising the simulator with %d thread(s)..." % (node_id, extra['threads']))
pop_size = len(index_exc)+len(index_inh)
pop_exc =  sim.Population(len(index_exc), sim.Izhikevich(a=0.02, b=0.2, c=-65, d=8, i_offset=0))
pop_inh = sim.Population(len(index_inh), sim.Izhikevich(a=0.02, b=0.25, c=-65, d=2, i_offset=0))
all_cells = pop_exc + pop_inh
assert len(all_cells) == (len(pop_exc) + len(pop_inh))

pop_pre_exc = all_cells[list(set(pre_exc))]
pop_post_exc = all_cells[list(set(post_exc))]
pop_pre_inh = all_cells[list(set(pre_inh))]
pop_post_inh =  all_cells[list(set(post_inh))]
print(pop_pre_exc)

assert len(pop_pre_exc) !=0
assert len(pop_pre_inh) !=0

# In[72]:

for pe in pop_exc:
    r = random.uniform(0.0, 1.0)
    pe.set_parameters(a=0.02, b=0.2, c=-65+15*r, d=8-r**2, i_offset=0)

for pe in pop_inh:
    r = random.uniform(0.0, 1.0)
    pe.set_parameters(a=0.02+0.08*r, b=0.2-0.05*r, c=-65, d= 2, i_offset=0)

index_exc = [ i for i,d in enumerate(dfm) if '-' in d[0] ]
index_inh = [ i for i,d in enumerate(dfm) if '+' in d[0] ]

NEXC = len(index_exc)
NINH = len(index_inh)
internal_conn_e = sim.ArrayConnector(plot_excit)
internal_conn_i = sim.ArrayConnector(plot_inhib)

ec = [ i for i in range(0,len(plot_excit)) ]
ic = [ i for i in range(0,len(plot_inhib)) ]

all_exc = all_cells[ec]
all_inh = all_cells[ic]


ohub_index = 0
for x,i in enumerate(plot_excit):
    row_sum = np.sum(i)
    if ohub_index < row_sum:
        ohub_index = x
'''
ihub_index = 0
for x,i in enumerate(plot_excit):
    row_sum = np.column(i)
    if ihub_index < row_sum:
        ihub_index = x
'''


rng = NumpyRNG(seed=64754)
exc_distr = RandomDistribution('normal', [5.125, 10e-1], rng=rng)
exc_syn = sim.StaticSynapse(weight=exc_distr, delay=delay_distr)

prj_exc_exc = sim.Projection(all_exc, all_exc, internal_conn_e, exc_syn, receptor_type='excitatory')
inh_distr = RandomDistribution('normal', [5e-2, 2.1e-3], rng=rng)

inh_syn = sim.StaticSynapse(weight=inh_distr, delay=delay_distr)
rng = NumpyRNG(seed=64754)
delay_distr = RandomDistribution('normal', [50, 100e-3], rng=rng)
prj_exc_exc = sim.Projection(all_inh, all_inh, internal_conn_i, inh_syn, receptor_type='inhibitory')

# Variation in propogation delays are very important for self sustaininig network activity.
# more so in point neurons which don't have internal propogation times.

stdp = STDPMechanism(
          weight=3.0, #0.02,  # this is the initial value of the weight
          delay="0.2 + 0.01*d",
          timing_dependence=SpikePairRule(tau_plus=20.0, tau_minus=20.0,
                                          A_plus=0.01, A_minus=0.012),
          weight_dependence=AdditiveWeightDependence(w_min=0.01, w_max=10.0))


first_set = set(pre_exc)
second_set = set(post_exc)
exc_targets = all_cells[pre_exc]
exc_srcs = all_cells[post_exc]
inh_srcs = all_cells[pre_inh] # = []
inh_targets = all_cells[post_inh] # = []
exc_cells = all_cells[index_exc]
inh_cells = all_cells[index_inh]

ext_stim = sim.Population(len(all_cells), sim.SpikeSourcePoisson(rate=7.5, duration=5000.0), label="expoisson")
rconn = 0.9
ext_conn = sim.FixedProbabilityConnector(rconn)
ext_syn = sim.StaticSynapse(weight=1.925)
connections = {}
connections['ext'] = sim.Projection(ext_stim, all_cells, ext_conn, ext_syn, receptor_type='excitatory')
##
# Setup and run a simulation. Note there is no current injection into the neuron.
# All cells in the network are in a quiescent state, so its not a surprise that xthere are no spikes
##

neurons = all_cells
sim = pyNN.neuron
arange = np.arange
import re
from pyNN.utility.plotting import Figure, Panel


neurons.record(['v','spikes'])  # , 'u'])
neurons.initialize(v=-65.0, u=-14.0)


# === Run the simulation =====================================================

sim.run(6000.0)

data = neurons.get_data().segments[0]
with open('pickles/qi.p', 'wb') as f:
    pickle.dump(data,f)

from pyNN.utility.plotting import Figure, Panel, comparison_plot, plot_spiketrains
data = neurons.get_data().segments[0]
v = data.filter(name="v")
for i in v:
  Figure(
    Panel(i, ylabel="Membrane potential (mV)", xticks=True,
          xlabel="Time (ms)", yticks=True),
    #Panel(u, ylabel="u variable (units?)"),
    annotations="Simulated with"
  )
#Figure.savefig('voltage_time.png')

import pickle

#data = neurons.get_data().segments[0]
v0 =  neurons[(0,)].get_data().segments[0].filter(name="v")[0]
v1 =  neurons[(1,)].get_data().segments[0].filter(name="v")[0]
#plt.clf()
plt.plot(v0,range(0,len(v0)))
plt.plot(v1,range(0,len(v0)))
plt.show()

def plot_spiketrains(segment):
  """
  Plots the spikes of all the cells in the given segments
  """
  for spiketrain in segment.spiketrains:
      print(spiketrain)
      y = np.ones_like(spiketrain) * spiketrain.annotations['source_id']
      plt.plot(spiketrain, y, 'b')
      plt.ylabel('Neuron number')
      plt.xlabel('Spikes')
  plt.savefig('raster_plot.png')
spikes = neurons.get_data("spikes").segments[0]
data = neurons.get_data().segments[0]
plot_spiketrains(data)


Figure(
    Panel(v0, ylabel="Membrane potential (mV)", xticks=True,
          xlabel="Time (ms)", yticks=True),
    #Panel(u, ylabel="u variable (units?)"),
    annotations="Simulated with"
)

Figure(
    Panel(v1, ylabel="Membrane potential (mV)", xticks=True,
          xlabel="Time (ms)", yticks=True),
    #Panel(u, ylabel="u variable (units?)"),
    annotations="Simulated with"
)
