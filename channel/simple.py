from numpy.random import rand

class SimpleChannel():
    def __init__(self, p_bad=0.2, p_drop_good=0.1, p_drop_bad=0.8):
        self.p_traffic = p_traffic
        self.p_drop_bad = p_drop_bad
        self.p_drop_good = p_drop_good

    def iterate(self):
        p1 = rand()
        self.is_bad = p1 <= self.p_bad

    def transmission_success(self, data_size):
        '''Does the transmission succeed'''
        p2 = rand()

        if self.is_bad:
            return p2 > self.p_drop_bad
        else:
            return p2 > self.p_drop_good
