#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run rasim batchly

Created on Wed Nov 12 02:50:02 2014

@author: Mehmet Emre
"""

import subprocess

output_dir = 'data'

N_runs = 30
t_total = 6000
N_agents = [5, 10, 50]
N_good_channels = [2, 5, 8]
buffer_levels = [2, 4, 10]
buffer_size = 1024
packet_size = 1024
min_packet_rate = 0
max_packet_rate = 6
beta_idles = [1, 2, 4]

total_runs = len(N_agents) * len(N_good_channels) * len(buffer_levels) * len(beta_idles)
current_run = 1

for N_agent in N_agents:
    for N_good_channel in N_good_channels:
        for buffer_level in buffer_levels:
            for beta_idle in beta_idles:
                p = subprocess.Popen(('python sim.py --N-runs %d --t-total %d --individual-q --random-channel\
                --highest-snr --output-dir %s --n-agent %d --n-good-channel %d --buffer-levels %d --buffer-size %d\
                --batch-run --packet-size %d --min-packet-rate %d --max-packet-rate %d --beta-idle %d' % (
                    N_runs, t_total, output_dir, N_agent, N_good_channel, buffer_level, buffer_size, packet_size,
                    min_packet_rate, max_packet_rate, beta_idle
                )).split())
                p.wait()
                print "[RUN #%d of %d completed]" % (current_run, total_runs)
                current_run += 1