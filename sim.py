#!/usr/bin/env python

from numpy import *
import matplotlib as mpl

from agent.best_channel import BestChannel
from channel.simple import SimpleChannel
from traffic.simple import SimpleTraffic
from environment import Environment

# simulation parameters:

# number of runs
N_runs = 10
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
# sensing time
T_sense = 0.01
# time slot
T_slot = 0.1
# transmission time
T_tx = T_slot - T_sense

# generate channel-related stuff
channels = [SimpleChannel() for i in xrange(N_channel)]
traffics = [SimpleTraffic() for i in xrange(N_channel)]

env = Environment(channels, traffics, pd=0.9, pf=0.1)

def init_state():
    # disk point picking - http://mathworld.wolfram.com/DiskPointPicking.html
    r = sqrt(random.rand()*r_init)
    theta = random.rand()*2*pi
    return {'state': (random.randint(0, N_channel), random.randint(0, B)), 'x': r*cos(theta), 'y':r*sin(theta)}

# generate agents
agents = [BestChannel(env, init_state(), 0.1, 1e3) for i in xrange(N_agent)]
env.set_agents(agents)

for n_run in xrange(N_runs):
    print "Run #%d" % n_run
    rates = [0,0,0]
    for t in xrange(t_total):
        env.next_slot()
        # get actions
        actions = [a.act() for a in agents]
        # TODO: get PU collisions, SU collisions, use channel state etc.
        # collisions per channel
        #
        # N_agent: PU collision, (0..N_agent-1): SU collision with ID
        # -1: No collision
        collisions = [N_agent if t else -1 for t in env.t_state]
        collided = [False] * N_agent
        for i, a in enumerate(actions):
            if a['action'] == 'transmit':
                if collisions[a['channel']] == N_agent:
                    # collision with PU, mark agent as collided
                    collided[i] = True
                elif collisions[a['channel']] >= 0:
                    # collision with SU, mark both agents as collided
                    collided[i] = collided[collisions[a['channel']]] = True
                else:
                    # no collision *yet*
                    collisions[a['channel']] = i
        
        # For each agent compute transmission successes and report
        # transmission success/failure to agent
        for i, a in enumerate(agents):
            # if collision occurred, report collusion
            if collided[i]:
                a.feedback(collision=True, success=False)
                rates[0] += 1
                continue
            act = actions[i]            
            ch = env.channels[act['channel']]
            # no collision, check transmission success by channel quality
            if ch.transmission_success(act['power'], T_tx, act['bits']):
                a.feedback(collision=False, success=True)
                rates[1] += 1
            else:
                a.feedback(collision=False, success=False)
                rates[2] += 1
    print "Collisions: %d, Successes: %d, Failures: %d" % tuple(rates)