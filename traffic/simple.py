import numpy as np

class SimpleTraffic():
    def __init__(self):
        self.q = np.array([1, 0]) if np.random.rand() > 0.5 else np.array([0, 1])
        self.traffic_probs = [0.3, 1]
        self.A = np.array([
            [0.9, 0.1],
            [0.3, 0.7]
        ]).transpose()

    def traffic_exists(self):
        '''Generate traffic with an HMM'''
        if np.random.rand() <= self.A.dot(self.q)[0]:
            self.q = np.array([1, 0])
        else:
            self.q = np.array([0, 1])
        return np.random.rand() <= self.q.dot(self.traffic_probs)
