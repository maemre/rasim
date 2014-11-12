from .base import BaseAgent
from numpy import fromiter, random, minimum, array, inf, isinf, abs
import params

class OptHighestSNR(BaseAgent):
    '''An agent that "chooses" the channel with lowest noise (or highest SNR) automatically'''
        
    def act(self):
        '''Return an action for current state. Choose channel with lowest drop-rate and
        send over that channel. If there are multiple of such channels, choose randomly.'''
        super(OptHighestSNR, self).act()
        ch = self.env.channels
        # get minimum noise (normally I'd use a filter+reduce, but this seems faster)
        try:
            min_noise = array([c.noise for i, c in enumerate(ch) if not self.env.t_state[i]]).min()
        # if all channels are occupied, stay idle for whole period   
        except ValueError:
            return self.idle()
        # get minimum noised channels
        min_noises = [i for i, c in enumerate(ch) if not self.env.t_state[i] and c.noise <= min_noise]
        # choose a random channel among them, and switch that channel
        chan = random.choice(min_noises)
        self.switch(chan)
        self.sense()
        P_tx = params.P_levels[-1]
        # send remaining packets in buffer
        pkgs_to_send = int((self.t_remaining * self.env.channels[chan].capacity(P_tx)) / params.pkg_size)

        if self.B - self.B_empty < pkgs_to_send:
            pkgs_to_send = self.B - self.B_empty

        if pkgs_to_send == 0:
            return self.idle()
            
        return self.transmit(P_tx, pkgs_to_send)
