# -*- coding: utf-8 -*-
"""
Created on Wed Nov  5 01:18:59 2014

@author: Mehmet Emre
"""

from .base import BaseAgent
from numpy import random
import params

class RandomChannel(BaseAgent):
    '''An agent that chooses a random channel and transmits over that channel.'''

    def act(self):
        '''Return an action for current state. Choose a random channel and
        transmit over that channel. If there are multiple of such channels,
        choose randomly.'''
        super(RandomChannel, self).act()
        
        # choose a random channel
        chan = random.randint(0, len(self.env.channels))
        self.switch(chan)
        # if there is traffic detected on the channel, stay idle
        if self.sense():
            return self.idle()
        P_tx = random.choice(params.P_levels)
        pkgs_to_send = int((self.t_remaining * self.env.channels[chan].capacity(P_tx)) / params.pkg_size)

        if self.B - self.B_empty < pkgs_to_send:
            pkgs_to_send = self.B - self.B_empty

        if pkgs_to_send == 0:
            return self.idle()
        # transmit with a random power choice
        return self.transmit(P_tx, pkgs_to_send)