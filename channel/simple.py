from numpy.random import rand
from scipy.special import erfc
from numpy import sqrt

class SimpleChannel():
    def __init__(self, p_bad=0.2, good_noise=0.01, bad_noise=0.01):
        self.p_bad = p_bad
        self.good_noise = good_noise
        self.bad_noise = bad_noise

    def iterate(self):
        p1 = rand()
        self.is_bad = p1 <= self.p_bad

    def transmission_success(self, power, t, data_size):
        '''Does the transmission succeed?
        Arguments:
        power : Transmission power
        t : transmission time
        data_size : Size of data to be transmitted in bits'''
        p2 = rand()
        # energy per bit
        E_b = power * t / data_size
        success_rate = (1 - self.berawgn(E_b)) ** data_size
        
        return p2 <= success_rate
    
    def noise(self):
        '''Return noise power spectral density.'''
        return self.good_noise if self.is_bad else self.bad_noise
    
    def berawgn(self, E_b):
        '''Get BER of channel by calculationg SNR. Assuming we're using
        BPSK with AWGN.
        Arguments:
        E_b : Energy per bit'''
        N_0 = self.noise()
        return 0.5 * erfc(sqrt(E_b / N_0))