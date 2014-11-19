import numpy as np

q0 = np.array([1, 0])
q1 = np.array([0, 1])
dq = q1 - q0
A = np.array([
    [0.9, 0.1],
    [0.4, 0.6]
]).transpose()
traffic_probs = [0.3, 0.7]

class SimpleTraffic(object):
    # fix slots to make access fast

    __slots__ = ['q_0']
    def __init__(self):
        #self.q = np.array([1, 0]) if np.random.rand() > 0.5 else np.array([0, 1])
        # is traffic state q_0?
        # faster computation trick for HMM
        self.q_0 = np.random.rand() > 0.5
        
    def traffic_exists(self):
        '''Generate traffic with HMM by making an iteration'''
        # generate new state
        self.q_0 = np.random.rand() <= (A[0, 0] if self.q_0 else A[1, 0])
        # generate traffic
        return np.random.rand() <= traffic_probs[0 if self.q_0 else 1] # the fastest way, chosen empirically
