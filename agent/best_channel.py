from .base import BaseAgent

class BestChannel(BaseAgent):
    '''An agent that "chooses" the channel with lowest package drop rate automatically'''

    def __init__(self, env, s0, P_t, max_bits):
        super(BestChannel, self).__init__(env, s0)
        self.P_t = P_t
        self.max_bits = max_bits

    def act(self):
        '''Return an action for current state. Choose channel with lowest drop-rate and
        send over that channel.'''
        ch = self.env.channels
        rate, channel = min((ch[i].noise(), i) for i in xrange(len(ch)))
        return {
            'action': 'transmit',
            'channel': channel,
            'power': self.P_t,
            'bits': self.max_bits}
    
    def feedback(self, *args, **kwargs):
        pass