from numpy.random import *

class Environment():
    def __init__(self, channels, traffics, pd, pf):
        self.channels = channels
        self.traffics = traffics
        self.pd = pd
        self.pf = pf

    def set_agents(self, agents):
        self.agents = agents

    def next_slot(self):
        for c in self.channels:
            c.iterate()
        self.t_state = [t.traffic_exists() for t in self.traffics]

    def detect_traffic(self, chan):
        '''Detect channel chan'''
        p = rand()

        if self.t_state[chan]:
            return p < self.pd
        else:
            return p < self.pf
