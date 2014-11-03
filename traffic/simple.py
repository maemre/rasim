from numpy.random import rand

class SimpleTraffic():
    def __init__(self, p_traffic=0.2):
        self.p_traffic = p_traffic

    def traffic_exists(self):
        '''Generate traffic with probability p_traffic'''
        return rand() <= self.p_traffic
