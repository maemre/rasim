# -*- coding: utf-8 -*-
"""
Created on Tue Nov  4 17:56:36 2014

@author: Mehmet Emre
"""

from util import to_dbm
import numpy as np
from args import argv

# Simulation parameters:
batch_run = bool(argv.batch_run)
# number of runs
N_runs = argv.N_runs
# total simulation time (as time slots)
t_total = argv.t_total
# total number of agents
N_agent = argv.n_agent
# number of channels
N_channel = 10
# number of good channels
N_good_channel = argv.n_good_channel
# radius of initial map
r_init = 5000

# Buffer parameters

# number of buffer slots
B = argv.buffer_size # packets
# Size of a buffer slot (also packet size)
pkg_size = argv.packet_size # bits
# buffer size in bits
b_size = B * pkg_size
# package rate for buffer traffic
# defined as a discrete uniform distribution with parameters:
pkg_min = argv.min_packet_rate # pkg / slot, inclusive
pkg_max = argv.max_packet_rate # pkg / slot, inclusive

# Power
P_tx = 200e-3 # W
P_levels = [0.75*P_tx, P_tx, 2*P_tx]
P_sense = 0.5*P_tx
P_sw = 0.5*P_tx
P_idle = 0.1*P_tx
P_rec = 40 # W

# durations
t_slot = 10e-3 # s
t_sense = 0.1 * t_slot
t_sw = 0.05 * t_slot # chan

# channel parameters
base_freq = 9e8 # 900 MHz
chan_bw = 1e6 # 1 MHz
# state transition probabilities, first state is good state
chan_trans_prob = np.array([
            [0.95, 0.05],
            [0.4, 0.6]
        ])
# channel noises
noise = {
    # overall worse channels
    'bad': {'good_noise': to_dbm(P_tx/chan_bw) - 65, 'bad_noise': to_dbm(P_tx/chan_bw) - 55, 'transition_probs': chan_trans_prob}, # Noise power density (dBm) x2, probability
    # overall better channels
    'good': {'good_noise': -174, 'bad_noise': to_dbm(P_tx/chan_bw) - 60, 'transition_probs': chan_trans_prob}, # Noise power density (dBm) x2, probability
}

del np # do not export np

prefix = "%d-%d-%d-%d-%d-%d-%d-%f" % (N_runs, t_total, N_agent, N_channel, N_good_channel, B, pkg_size, argv.beta_idle)

# constants to be used instead of strings
class ACTION:
    TRANSMIT, IDLE = range(2)