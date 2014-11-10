# -*- coding: utf-8 -*-
"""
Created on Wed Nov  5 01:18:59 2014

@author: Mehmet Emre
"""

from .base import BaseAgent
from numpy import ceil, random
import params

class FixChannel(BaseAgent):
    '''An agent that chooses a random channel and transmits over that channel.'''

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.load = int(ceil(params.N_agent * 1.0 / params.N_channel))
        self.run_this_turn = self.id % self.load
    def act(self):
        '''Return an action for current state. Choose a random channel and
        transmit over that channel. If there are multiple of such channels,
        choose randomly.'''
        super(self.__class__, self).act()
        
        # choose channel by agent id
        chan = self.id / self.load
        self.switch(chan)
        # skip turns:
        self.run_this_turn = (self.run_this_turn + 1) % self.load
        if self.run_this_turn != 0:
            return self.idle()
        # if there is traffic detected on the channel, stay idle
        if self.sense():
            return self.idle()

        pkgs_to_send = int((self.t_remaining * params.bitrate) / params.pkg_size)

        if self.B - self.B_empty < pkgs_to_send:
            pkgs_to_send = self.B - self.B_empty

        if pkgs_to_send == 0:
            return self.idle()
            
        return self.transmit(random.choice(params.P_levels), pkgs_to_send)