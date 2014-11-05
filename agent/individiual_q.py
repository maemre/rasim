# -*- coding: utf-8 -*-
"""
Created on Wed Nov  5 01:18:59 2014

@author: Mehmet Emre
"""

from .base import BaseAgent
from numpy import random

class IndQAgent(BaseAgent):
    '''An agent that chooses a random channel and transmits over that channel.'''

    def __init__(self, env, s0, P_tx, max_bits):
        super(IndQAgent, self).__init__(env, s0)
        self.P_tx = P_tx
        self.max_bits = max_bits

    def act(self):
        '''Return an action for current state. Choose a random channel and
        transmit over that channel. If there are multiple of such channels,
        choose randomly.'''
        super(IndQAgent, self).act()
        
        # choose a random channel
        chan = random.randint(0, len(self.env.channels))
        self.switch(chan)
        # if there is traffic detected on the channel, stay idle
        if self.sense():
            return self.idle()

        pkgs_to_send = self.max_bits / params.pkg_size

        if self.B - self.B_empty < self.max_bits / params.pkg_size:
            pkgs_to_send = self.B - self.B_empty

        if pkgs_to_send == 0:
            return self.idle()

        bits_to_send = pkgs_to_send * params.pkg_size
        bitrate = bits_to_send / self.t_remaining
        return self.transmit(self.P_tx, pkgs_to_send, bitrate)
