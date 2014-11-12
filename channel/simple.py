from numpy.random import rand
from numpy import sqrt, exp, pi, log1p, log, log2
import params
from util import *

c = 3e8 # speed of light

class SimpleChannel:
    def __init__(self, freq, transition_probs, good_noise, bad_noise):
        # channel frequency
        self.freq = freq
        # convert noise from dBm to W
        self.good_noise = to_watt(good_noise)
        self.bad_noise = to_watt(bad_noise)
        # set transition probabilities, first state is good state
        self.A = transition_probs
        self.is_bad = rand() <= 0.5 # priors are uniform
        
    def iterate(self):
        self.is_bad = rand() <= self.A[1,1] if self.is_bad else self.A[0,1]
        self.noise = (self.bad_noise if self.is_bad else self.good_noise) * params.chan_bw

    def transmission_successes(self, power, bitrate, pkt_size, n_pkt, x, y):
        '''How many packets have been successfully transmitted?
        Arguments:
        power : Transmission power
        t : transmission time
        data_size : Size of data to be transmitted in bits'''
        # apply Friis transmission eqn to get received power
        d = sqrt(x ** 2 + y ** 2) # distance to BS
        P_r = power * (c / (4 * pi * d * self.freq))
        # energy per bit
        t = n_pkt * pkt_size / bitrate
        E_b = P_r * t / pkt_size
        success_rate = exp(log1p(-self.berawgn(E_b)) * pkt_size)
        
        return int((rand(n_pkt) <= success_rate).sum())

    def capacity(self, P_tx):
        return params.chan_bw * log2(1 + P_tx/self.noise)
    
    def berawgn(self, E_b):
        '''Get BER of channel by calculationg SNR. Assuming we're using
        DBPSK with AWGN.
        Arguments:
        E_b : Energy per bit'''
        N_0 = self.bad_noise if self.is_bad else self.good_noise
        return 0.5 * exp(-(E_b / N_0))