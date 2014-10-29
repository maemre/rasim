from .base import BaseAgent

class GreedyAgent(BaseAgent):

    def __init__(self, env, s0):
        super(GreedyAgent, self).__init__(env, s0)

    def act(self, state):
        '''Return an action for current state.'''
        # constantly try to transmit data over same channel
        return ('transmit', self.chan)
