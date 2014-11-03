from .base import BaseAgent

class BestChannel(BaseAgent):
    '''An agent that "chooses" the channel with lowest package drop rate automatically'''

    def __init__(self, env, s0):
        super(BestChannel, self).__init__(env, s0)

    def act(self):
        '''Return an action for current state. Choose channel with lowest drop-rate and
        send over that channel.'''
        ch = self.env.channels
        rate, channel = max((ch[i].drop_rate(), i) for i in xrange(len(ch)))
        return {'action': 'transmit', 'channel': channel}