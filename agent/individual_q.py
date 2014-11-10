# -*- coding: utf-8 -*-
"""
Created on Wed Nov  5 01:18:59 2014

@author: Mehmet Emre
"""

from .base import BaseAgent
import numpy as np
import params

# parameters

beta_idle = 4 # coefficient cost of staying idle
beta_md = 0.4 # misdetection punishment coefficient
beta_loss = 0.1 # punishment for data loss in channel
alpha = 0.6 # learning rate
eps = 0.03 # exploration probability
discount = 0.05 # discount factor, gamma
# coefficient for normalizing b/E to energies
K = (params.P_tx * params.t_slot) ** 2  / (params.bitrate * params.t_slot)

class IndividualQ(BaseAgent):
    '''An agent that chooses a random channel and transmits over that channel.'''
    
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        # state = (current channel, buffer level)
        # action = (transmit, channel, power level) + (idle)
        # but representing (idle) is hard here, we're representing transmit
        # by multiplying channel with power level, so idle=N_channel*len(P_levels)

        # initialize Q-values to random values in a good range   
        self.Q = np.random.rand(
            
            params.N_channel,
            params.B + 1,
            params.N_channel * len(params.P_levels) + 1 # this is actions
        ) * params.P_tx * params.t_slot * 10
        
        self.idle_action = params.N_channel * len(params.P_levels)

    def policy(self):
        # epsilon part of epsilon-greedy
        if np.random.rand() < eps:
            return np.random.randint(0, params.N_channel * len(params.P_levels) + 1)
        # the greedy part - choose max. action
        return self.Q[self.chan, self.B_empty].argmax()
        
    def act(self):
        '''Return an action for current state. Choose a random channel and
        transmit over that channel. If there are multiple of such channels,
        choose randomly.'''
        super(self.__class__, self).act()
        
        # choose an action by policy
        self.a = self.policy()
        # store old state for feedback
        self.state = (self.chan, self.B_empty)
        
        if self.a == self.idle_action:
            return self.idle()
        
        # get channel from action
        chan = self.a / len(params.P_levels)
        # switch to channel
        self.switch(chan)
        # if there is traffic detected on the channel, stay idle
        if self.sense():
            return self.idle()

        pkgs_to_send = int((self.t_remaining * params.bitrate) / params.pkg_size)

        if self.B - self.B_empty < pkgs_to_send:
            pkgs_to_send = self.B - self.B_empty

        if pkgs_to_send == 0:
            return self.idle()
            
        return self.transmit(params.P_levels[self.a/params.N_channel], pkgs_to_send)
    
    def feedback(self, collision, success, idle=False):
        super(self.__class__, self).feedback(collision, success, idle)
        r = 0
        if idle:
            # agent stayed idle
            r = - beta_idle * self.E_slot
        elif success:
            # successful transmission, r = K * bits/J ~= J
            r = K * (params.pkg_size) / self.E_slot
        elif collision:
            # collision (not necessarily with PU)
            r = - beta_md * self.E_slot
        else:
            # package lost in channel
            r = - beta_loss * self.E_slot
        self.Q[self.state[0], self.state[1], self.a] += alpha * (r + discount * self.Q[self.chan, self.B_empty].max() - self.Q[self.state[0], self.state[1], self.a])