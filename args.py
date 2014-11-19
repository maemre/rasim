# -*- coding: utf-8 -*-
"""
Created on Mon Nov 10 17:14:37 2014

@author: Mehmet Emre

Parser for command-line arguments, params will use this for setting it's values.
"""

import argparse

parser = argparse.ArgumentParser(description="rasim - A radio network simulator")
parser.add_argument('--batch-run', action='store_true', help='run simulator in batch-mode, no graph windows will be produced')
parser.add_argument('--N-runs', action='store', default=10, help='number of runs per agent', type=int)
parser.add_argument('--t-total', action='store', default=6000, help='total simulation time (time slots) per run, default = 6000', type=int)
parser.add_argument('--individual-q', action='append_const', dest='agents', const='IndividualQ', help='run individual Q-learning agents')
parser.add_argument('--random-channel', action='append_const', dest='agents', const='RandomChannel', help='run randomly channel selecting agents')
parser.add_argument('--highest-snr', action='append_const', dest='agents', const='OptHighestSNR', help='run agents selecting constant')
parser.add_argument('--output-dir', action='store', default='data/', help='set output directory, it must be already created')
parser.add_argument('--n-agent', action='store', default=5, help='number of agents', type=int)
parser.add_argument('--n-stationary', action='store', help='number of stationary agents', type=int)
parser.add_argument('--n-good-channel', action='store', default=5, help='number of good (type-1) channels among 10 channels', type=int)
parser.add_argument('--buffer-size', action='store', default=512, help='size of buffer, default: 1024 packets', type=int)
parser.add_argument('--buffer-levels', action='store', default=10, help='# of buffer levels in Q-learning, default: 10', type=int)
parser.add_argument('--packet-size', action='store', default=1024, help='size of a packet, default: 1024 bits', type=int)
parser.add_argument('--min-packet-rate', action='store', default=0, help='minimum packet rate per timeslot per agent, default = 0', type=int)
parser.add_argument('--max-packet-rate', action='store', default=6, help='maximum packet rate per timeslot per agent, default = 6', type=int)
parser.add_argument('--beta-idle', action='store', default=10, help='cost coefficient of staying idle for Q Learning default = 4', type=float)

parser.add_argument('--verbose', action='store_true', help='increase verbosity, give statistics about each run')
parser.add_argument('-v', '--version', action='version', version='%(prog)s 2.0')
argv = parser.parse_args()
