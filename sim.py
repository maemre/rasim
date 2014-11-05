#!/usr/bin/env python

# Holy import!
from __future__ import division

from numpy import *

from agent import OptHighestSNR, RandomChannel
from channel.simple import SimpleChannel
from traffic.simple import SimpleTraffic
from environment import Environment

# simulation parameters:
from params import *

# generate channel-related stuff
channels = [SimpleChannel(freq=base_freq + chan_bw * i) for i in xrange(N_channel)]
traffics = [SimpleTraffic() for i in xrange(N_channel)]

env = Environment(channels, traffics, pd=0.9, pf=0.1)

def init_state(i):
    # disk point picking - http://mathworld.wolfram.com/DiskPointPicking.html
    r = sqrt(random.rand())*r_init
    theta = random.rand()*2*pi
    return {'state': (random.randint(0, N_channel), random.randint(0, B)), 'x': r*cos(theta), 'y':r*sin(theta), 'id': i}

# generate agents

# OptHighestSNR agents
agent_type = RandomChannel
agents = [agent_type(env, init_state(i), P_tx=0.2, max_bits=2**14) for i in xrange(N_agent)]
env.set_agents(agents)

for n_run in xrange(N_runs):
    print "Run #%d" % n_run
    rates = [0,0,0,0]
    for t in xrange(t_total):
        env.next_slot()
        # get actions
        actions = [a.act() for a in agents]
        # collisions per channel where,
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
            if act['action'] != 'transmit':
                rates[3] += 1
                continue
            ch = env.channels[act['channel']]
            # no collision, check transmission success by channel quality
            if ch.transmission_success(act['power'], T_tx, act['bits'], a.x, a.y):
                a.feedback(collision=False, success=True)
                rates[1] += 1
            else:
                a.feedback(collision=False, success=False)
                rates[2] += 1
    print "Collisions: %d\nSuccesses: %d\nLost in Channel: %d\nIdle: %d" % tuple(rates)
    print "%Success:", rates[1]/(t_total*N_agent - rates[3]) * 100
    print "%Collided channels:", rates[0]/(t_total*N_channel) * 100
