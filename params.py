# -*- coding: utf-8 -*-
"""
Created on Tue Nov  4 17:56:36 2014

@author: Mehmet Emre
"""

# Simulation parameters:


# number of runs
N_runs = 10
# total simulation time (as time slots)
t_total = 1000
# number of agents
N_agent = 3
# number of channels
N_channel = 10
# radius of initial map
r_init = 5000

# Buffer parameters

# number of buffer slots
B = 50
# Size of a buffer slot (also packet size)
pkg_size = 1024 # bits
# buffer size in bits
b_size = B * pkg_size
# package rate for buffer traffic
# defined as a discrete uniform distribution with parameters:
pkg_min = 0 # pkg / slot, inclusive
pkg_max = 6 # pkg / slot, inclusive

# Power
P_tx = 200e-3 # W
P_levels = [0.75*P_tx, P_tx, 2*P_tx]
P_sense = 0.5*P_tx
P_sw = 0.5*P_tx
P_idle = 0.4*P_tx
P_rec = 40 # W

# durations
t_slot = 10e-3 # s
t_sense = 0.1 * t_slot
t_sw = 0.05 * t_slot # chan

# channel parameters
base_freq = 9e8 # 900 MHz
chan_bw = 1e5 # 100 KHz
noise = {'good': -100, 'bad': -80} # Noise power density (dBm)