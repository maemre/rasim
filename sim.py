#!/usr/bin/env python

# Holy import!
from __future__ import division

from numpy import *
from matplotlib import pyplot as P
from agent import OptHighestSNR, RandomChannel, IndividualQ, FixChannel
from channel.simple import SimpleChannel
from traffic.simple import SimpleTraffic
from environment import Environment
import os
# simulation parameters:
from params import *
from args import argv

# create data-output directory
output_dir = os.path.join(argv.output_dir, prefix)
try:
    os.mkdir(argv.output_dir)
except OSError:
    pass
try:
    os.mkdir(output_dir)
except OSError:
    pass

# generate channel-related stuff
# goodness of channels
goodness = concatenate((ones(N_good_channel), zeros(N_channel - N_good_channel)))
random.shuffle(goodness)
# channel generator
def gen_chan(i):
    ch = noise['bad']
    if goodness[i]:
        ch = noise['good']
    return SimpleChannel(base_freq + chan_bw * i, **ch)

def init_state(i):
    # disk point picking - http://mathworld.wolfram.com/DiskPointPicking.html
    r = sqrt(random.rand())*r_init
    theta = random.rand()*2*pi
    return {'state': (random.randint(0, N_channel), random.randint(0, B)), 'x': r*cos(theta), 'y':r*sin(theta), 'id': i}

if argv.agents is None:
    print 'No agent type is specified. Simulation cannot run. For details run rasim with "--help" option'
    exit(1)

agent_types = []
for i in [RandomChannel, IndividualQ, OptHighestSNR]: # + [FixChannel, OptHighestSNR]
    if i.__name__ in argv.agents:
        agent_types.append(i)

paths = {}
for a in agent_types:
    paths[a] = os.path.join(output_dir, a.__name__)
    try:
        os.mkdir(paths[a])
    except OSError:
        pass

# init statistics
avg_energies = zeros([len(agent_types), N_agent, t_total])
en_type = zeros([len(agent_types), t_total])
avg_bits = zeros([len(agent_types), N_agent, t_total])
bits_type = zeros([len(agent_types), t_total], dtype=int_)
en_idle = zeros([len(agent_types), N_agent, t_total])
en_sense = zeros([len(agent_types), N_agent, t_total])
en_sw = zeros([len(agent_types), N_agent, t_total])
en_tx = zeros([len(agent_types), N_agent, t_total])
buf_overflow = zeros([len(agent_types), N_agent, t_total], dtype=int_)
buf_levels = zeros([len(agent_types), N_agent, t_total], dtype=int_)
init_positions = zeros([len(agent_types), N_runs, N_agent, 2])
last_positions = zeros([len(agent_types), N_runs, N_agent, 2])

def run_simulation(agent_type, agent_no):
    global avg_energies, en_type, avg_bits, bits_type, buf_overflow
    # channels themselves
    channels = [gen_chan(i) for i in xrange(N_channel)]
    # channel traffics
    traffics = [SimpleTraffic() for i in xrange(N_channel)]
    
    env = Environment(channels, traffics, pd=0.9, pf=0.1)
    if argv.verbose or not batch_run:
        print 'Agent type:', agent_type.__name__
    for n_run in xrange(N_runs):
        # generate agents
        agents = [agent_type(env, init_state(i)) for i in xrange(N_agent)]
        env.set_agents(agents)
        
        init_positions[agent_no, n_run] = [(a.x, a.y) for a in agents]
        energies = zeros([N_agent, t_total])
        bits = zeros([N_agent, t_total])
        if argv.verbose or not batch_run:
            print "Run #%d of %d(agent), %d of %d(total)" % (n_run + 1, N_runs, n_run + agent_no * N_runs + 1, N_runs * len(agent_types))
        rates = [0,0,0,0,0]
        for t in xrange(t_total):
            env.next_slot()
            # get actions
            actions = [a.act_then_idle() for a in agents]
            # collect statistics for buffer overflow and buffer levels
            for i, a in enumerate(agents):
                buf_overflow[agent_no, i, t] = int(a.buf_overflow)
                buf_levels[agent_no, i, t] += B - a.B_empty
            # collisions per channel where,
            # N_agent: PU collision, (0..N_agent-1): SU collision with ID
            # -1: No collision
            collisions = [N_agent if traffic else -1 for traffic in env.t_state]
            collided = [False] * N_agent
            for i, a in enumerate(actions):
                if a['action'] == ACTION.TRANSMIT:
                    if collisions[a['channel']] == N_agent:
                        # collision with PU, mark agent as collided
                        collided[i] = True
                        rates[4] += 1
                    elif collisions[a['channel']] >= 0:
                        # collision with SU, mark both agents as collided
                        collided[i] = collided[collisions[a['channel']]] = True
                    else:
                        # no collision *yet*
                        collisions[a['channel']] = i
            
            # For each agent compute transmission successes and report
            # transmission success/failure to agent
            for i, a in enumerate(agents):
                # collect energy usage statistics
                energies[i, t] = a.E_slot
                en_type[agent_no, t] += a.E_slot
                en_idle[agent_no, i, t] += a.E_idle
                en_sense[agent_no, i, t] += a.E_sense
                en_tx[agent_no, i, t] += a.E_tx
                en_sw[agent_no, i, t] += a.E_sw
                
                act = actions[i]
                # send feedback to idle agents too
                if act['action'] == ACTION.IDLE:
                    a.feedback(False, False, idle=True)
                # if collision occurred, report collusion
                if collided[i]:
                    a.feedback(collision=True, success=False)
                    rates[0] += 1
                    continue
                if act['action'] != ACTION.TRANSMIT:
                    rates[3] += 1
                    continue
                ch = env.channels[act['channel']]
                # no collision, check transmission success by channel quality
                pkt_sent = ch.transmission_successes(act['power'], act['bitrate'], act['pkt_size'], act['n_pkt'], a.x, a.y)
                # give feedback      
                if pkt_sent == 0:
                    a.feedback(collision=False, success=False)
                else:
                    a.feedback(collision=False, success=True, N_pkt=pkt_sent)
                rates[1] += pkt_sent * 1.0 / act['n_pkt']
                rates[2] += act['n_pkt'] - pkt_sent
                # collect bit transmission statistics
                bits[i, t] = pkt_sent * act['pkt_size']
                bits_type[agent_no, t] += pkt_sent * act['pkt_size']
        # save energies
        #savetxt('energy_%d.txt' % n_run, energies)
        # take averages
        avg_energies[agent_no] += energies
        avg_bits[agent_no] += bits
        # print stats
        rates[4] = rates[4] / (t_total * N_channel) * 100
        if argv.verbose or not batch_run:        
            print "Collisions: %d\nSuccesses: %f\nLost in Channel: %d\nIdle: %d\n%%PU Collisions: %f" % tuple(rates)
            print "%Success:", rates[1]/(t_total*N_agent - rates[3]) * 100
            print "%Collided channels:", rates[0]/(t_total*N_channel) * 100
            print
        
        last_positions[agent_no, n_run] = [(a.x, a.y) for a in agents]

for i, agent_type in enumerate(agent_types):
    run_simulation(agent_type, i)

buf_levels /= N_runs
avg_energies /= N_runs
avg_bits /= N_runs
en_idle /= N_runs
en_sense /= N_runs
en_tx /= N_runs
en_sw /= N_runs

# give outputs
if not batch_run:
    P.figure()
    
    for i, agent_type in enumerate(agent_types):
        P.plot(cumsum(en_type[i])/cumsum(bits_type[i]), label=agent_type.__name__)
    
    P.legend()
    P.xlabel('Time (time slots)')
    P.ylabel('Energy/bit (cumulative)')
    P.title('Efficiency (Cumulative Energy/bit) vs Time')
    
    P.figure()
    
    for i, agent_type in enumerate(agent_types):
        P.plot(convolve(buf_overflow[i].sum(axis=0)/(N_agent*1.0), [1./7]*7), label=agent_type.__name__)
    
    P.legend()
    P.xlabel('Time (time slots)')
    P.ylabel('# of buffer overflows (7-point avg, per agent)')
    P.title('Buffer Overflows vs Time')
    
    P.figure()
    P.bar(arange(len(agent_types)), buf_overflow.sum(axis=(1,2)))
    P.legend()
    P.xlabel('Agent Type')
    P.ylabel('# of buffer overflows (avg, per agent)')
    P.xticks(arange(len(agent_types) + 1), [x.__name__ for x in agent_types] + [''])
    P.title('Buffer overflows vs Agent Type')
    
    P.figure()
    
    for i, agent_type in enumerate(agent_types):
        P.plot(buf_levels[i].sum(axis=0)/(N_agent*1.0), label=agent_type.__name__)
    
    P.legend()
    P.xlabel('Time (time slots)')
    P.ylabel('buffer occupancy')
    P.title('Buffer Occupancy (avg) vs Time')
    
    P.figure()
    
    for i, agent_type in enumerate(agent_types):
        P.plot(cumsum(en_idle[i].sum(axis=0) / N_agent), label=agent_type.__name__)
    
    P.legend()
    P.xlabel('Time (time slots)')
    P.ylabel('Avg Idle Energy (cumulative)')
    P.title('Idle Energy vs Time')
    P.show()

    print "Throughput:"
    for i, agent_type in enumerate(agent_types):
        print "\t%s:\t%f" % (agent_type.__name__, sum(bits_type[i]))

# save statistics

# save agent types
with open(os.path.join(output_dir, 'agents.txt'), 'w') as f:
    f.write('\n'.join(x.__name__ for x in agent_types))
save(os.path.join(output_dir, 'avg_energies.npy'), avg_energies)
save(os.path.join(output_dir, 'avg_bits.npy'), avg_bits)
save(os.path.join(output_dir, 'en_idle.npy'), en_idle)
save(os.path.join(output_dir, 'en_sense.npy'), en_sense)
save(os.path.join(output_dir, 'en_tx.npy'), en_tx)
save(os.path.join(output_dir, 'en_sw.npy'), en_sw)
save(os.path.join(output_dir, 'en_type.npy'), en_type)
save(os.path.join(output_dir, 'buf_overflow.npy'), buf_overflow)
save(os.path.join(output_dir, 'buf_levels.npy'), buf_overflow)
save(os.path.join(output_dir, 'init_positions.npy'), init_positions)
save(os.path.join(output_dir, 'last_positions.npy'), last_positions)