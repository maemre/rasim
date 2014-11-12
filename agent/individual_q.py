# -*- coding: utf-8 -*-
"""
Created on Wed Nov  5 01:18:59 2014

@author: Mehmet Emre
"""

from .base import BaseAgent
import numpy as np
import params

# parameters

B = 10 # buffer levels
B_lvl_size = params.B / (B - 1) if params.B % (B - 1) else params.B / B + 1
beta_overflow = 1000
beta_idle = params.argv.beta_idle # coefficient cost of staying idle
beta_md = 0.4 # misdetection punishment coefficient
beta_loss = 1 # punishment for data loss in channel
eps = 0.03 # exploration probability
discount = 0.1 # discount factor, gamma
# coefficient for normalizing b/E to energies

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
            B,
            params.N_channel * len(params.P_levels) + 1 # this is actions
        ) * params.P_tx * params.t_slot
        
        # store number of visits to a state-action pair
        self.visit = np.zeros([
            params.N_channel,
            B,
            params.N_channel * len(params.P_levels) + 1 # this is actions
        ])       
        
        self.idle_action = params.N_channel * len(params.P_levels)

    def policy(self):
        # epsilon part of epsilon-greedy
        if np.random.rand() < eps:
            return np.random.randint(0, params.N_channel * len(params.P_levels) + 1)
        # the greedy part - choose max. action
        return self.Q[self.chan, self.B_empty / B_lvl_size].argmax()
        
    def act(self):
        '''Return an action for current state. Choose a random channel and
        transmit over that channel. If there are multiple of such channels,
        choose randomly.'''
        super(self.__class__, self).act()
        
        # choose an action by policy
        self.a = self.policy()
        # store old state for feedback
        self.state = (self.chan, self.B_empty / B_lvl_size)
        self.visit[self.chan, self.B_empty / B_lvl_size, self.a] += 1        
        
        if self.a == self.idle_action:
            return self.idle()
        
        # get channel from action
        chan = self.a / len(params.P_levels)
        # switch to channel
        self.switch(chan)
        # if there is traffic detected on the channel, stay idle
        if self.sense():
            return self.idle()
        
        self.P_tx = P_tx = params.P_levels[self.a/params.N_channel]
        bitrate = self.env.channels[chan].capacity(P_tx)
        pkgs_to_send = int((self.t_remaining * bitrate) / params.pkg_size)

        if self.B - self.B_empty < pkgs_to_send:
            pkgs_to_send = self.B - self.B_empty

        if pkgs_to_send == 0:
            return self.idle()
            
        return self.transmit(P_tx, pkgs_to_send)
    
    def alpha(self):
        "Learning rate, decreasing over time"
        return 0.2 + 0.8 / (1. + self.visit[self.state[0], self.state[1], self.a])
    
    def feedback(self, collision, success, idle=False, buf_overflow=False, N_pkt=0):
        super(self.__class__, self).feedback(collision, success, idle, buf_overflow, N_pkt)
        r = 0
        if buf_overflow:
            if self.a == self.idle_action:
                # buffer overflow occurred due to staying idle
                r = - beta_overflow * params.P_tx * params.t_slot # get punishment for buffer overflow
            else:
                return
            return # disable buffer overflow punishment for now
        elif idle:
            # agent stayed idle
            r = - beta_idle * self.E_slot
        elif success:
            # successful transmission, [r] = [K] * bits/J ~= J
            K = (self.P_tx) ** 2 * params.t_slot / self.env.channels[self.chan].capacity(self.P_tx) # we assume SNR=1, so chan_bw == bitrate for unit conversion
            r = K * (params.pkg_size) * N_pkt / self.E_slot
        elif collision:
            # collision (not necessarily with PU)
            r = - beta_md * self.E_slot
        else:
            # all packets lost in channel
            r = - beta_loss * self.E_slot
        self.Q[self.state[0], self.state[1], self.a] += self.alpha() * (r + discount * self.Q[self.chan, self.B_empty / B_lvl_size].max() - self.Q[self.state[0], self.state[1], self.a])