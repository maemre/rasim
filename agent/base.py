import abc
from numpy import *

class BaseAgent():
    '''A base class for all actors'''
    __metaclass__ = abc.ABCMeta
    # speed of random walk
    speed = 5

    def __init__(self, env, s0):
        '''Initialize actor using environment and initial state'''
        self.x = s0['x']
        self.y = s0['y']
        self.env = env
        self.chan, self.b = s0['state']

    @abstractmethod
    def act(self, state):
        '''Return an action for current state.'''
        pass

    def move(self, state):
        '''Make random walk in 2-d space with constant-speed jumps. Return the move'''
        phi = random.uniform(0, 2*pi)
        move = speed*cos(phi), speed*sin(phi)
        self.x += move[0]
        self.y += move[1]
        return move
