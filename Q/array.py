from numpy import *

class ArrayQ():
    '''Represent Q matrix as an array'''

    def __init__(self, n_channels, B, actions):
        '''Initialize State-Action Array.
        Arguments:
        n_channels : int - # of N_channels
        B : int - Buffer size (as packages)
        actions : tuple - actions'''
        self.Q = zeros([n_channels, B, len(actions)])
        self.action_dict = {actions[i]:i for i in xrange(len(actions))}
        self.actions = actions
        self.n_actions = len(actions)

    def max_action(self, channel, b):
        return self.actions[self.Q[channel, b].argmax()]
