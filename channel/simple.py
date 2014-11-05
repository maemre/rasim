from numpy.random import rand
from numpy import sqrt, exp, pi
import params

class SimpleChannel():
    def __init__(self, freq, p_bad=0.2, good_noise=params.noise['good'], bad_noise=params.noise['bad']):
        # channel frequency
        self.freq = freq
        self.p_bad = p_bad
        # convert noise from dBm to W
        self.good_noise = 10 ** ((good_noise - 30) / 10)
        self.bad_noise = 10 ** ((bad_noise - 30) / 10)

    def iterate(self):
        p1 = rand()
        self.is_bad = p1 <= self.p_bad

    def transmission_success(self, power, t, data_size, x, y):
        '''Does the transmission succeed?
        Arguments:
        power : Transmission power
        t : transmission time
        data_size : Size of data to be transmitted in bits'''
        p2 = rand()
        # apply Friis transmission eqn to get received power
        c = 3e8 # speed of light
        d = sqrt(x ** 2 + y ** 2) # distance to BS
        p_r = power * (c / (4 * pi * d * self.freq))
        # energy per bit
        E_b = p_r * t / data_size
        success_rate = (1 - self.berawgn(E_b)) ** data_size
        
        return p2 <= success_rate
    
    def noise(self):
        '''Return noise power spectral density.'''
        return self.good_noise if self.is_bad else self.bad_noise
    
    def berawgn(self, E_b):
        '''Get BER of channel by calculationg SNR. Assuming we're using
        DBPSK with AWGN.
        Arguments:
        E_b : Energy per bit'''
        N_0 = self.noise()
        return 0.5 * exp(-(E_b / N_0))