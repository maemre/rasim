from .base import BaseAgent
from numpy import random, min, array

class OptHighestSNR(BaseAgent):
    '''An agent that "chooses" the channel with lowest noise (or highest SNR) automatically'''

    def __init__(self, env, s0, P_tx, max_bits):
        super(OptHighestSNR, self).__init__(env, s0)
        self.P_tx = P_tx
        self.max_bits = max_bits

    def act(self):
        '''Return an action for current state. Choose channel with lowest drop-rate and
        send over that channel. If there are multiple of such channels, choose randomly.'''
        super(OptHighestSNR, self).act()
        p_send = 0.3 # only try to send data in 30% of the time
        if random.rand() > p_send:
            return { 'action': 'idle' }
        ch = self.env.channels
        # get noises
        noises = array([c.noise() for c in ch])
        # get minimum noise
        min_noise = min(noises)
        min_noises = array([i for i in xrange(len(noises)) if noises[i] <= min_noise])
        chan = random.choice(min_noises)
        # if there is traffic on the channel, stay idle
        if self.env.t_state[chan]:
            return self.idle()

        bitrate = self.max_bits / self.t_remaining
        return self.transmit(self.P_tx, self.max_bits, bitrate)
