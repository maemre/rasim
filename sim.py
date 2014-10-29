#!/usr/bin/env python

from numpy import *
import matplotlib as mpl

from agent.greedy import GreedyAgent
from channel.simple import SimpleChannel
from traffic.simple import SimpleTraffic
from environment import Environment

# simulation parameters:

# total simulation time (as time slots)
t_total = 100

# number of agents
N_agent = 30
# number of channels
N_channel = 10
# radius of initial map
r_init = 50
# number of buffer slots
B = 50

# generate channel-related stuff
channels = [SimpleChannel() for i in xrange(N_channel)]
traffics = [SimpleTraffic() for i in xrange(N_channel)]

env = Environment(channels, traffics)

def init_state():
    # disk point picking - http://mathworld.wolfram.com/DiskPointPicking.html
    r = sqrt(random.rand()*r_init)
    theta = random.rand()*2*pi
    return {'state': (random.randint(0, N_channel), random.randint(0, B)), 'x': r*cos(theta), 'y':r*sin(theta)}

# generate agents
agents = [GreedyAgent(env, init_state()) for i in xrange(N_agent)]
