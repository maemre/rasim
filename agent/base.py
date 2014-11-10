import abc
from numpy import *
import params

class BaseAgent():
    '''A base class for all actors'''
    __metaclass__ = abc.ABCMeta
    # speed of random walk (m/time_slot)
    speed = 5

    def __init__(self, env, s0):
        '''Initialize actor using environment and initial state'''
        self.x = s0['x']
        self.y = s0['y']
        self.id = s0['id']
        self.env = env
        self.chan, self.b = s0['state']
        self.energy = 0
        self.t_remaining = params.t_slot
        self.B = params.B
        self.B_empty = self.B
        self.buf_overflow = False

    def fill_buffer(self):
        pkgs = random.randint(params.pkg_min, params.pkg_max+1)
        if pkgs > self.B_empty:
            #print "Buffer overflow at agent ", self.id
            self.buf_overflow = True
        else:
            self.buf_overflow = False            
            self.B_empty -= pkgs

    @abc.abstractmethod
    def act(self):
        '''Return an action for current state.'''
        self.fill_buffer()
        self.n_pkg_slot = 0
        self.t_remaining = params.t_slot
        self.E_slot = 0
        pass

    def move(self):
        '''Make random walk in 2-d space with constant-speed jumps. Return the move'''
        phi = random.uniform(0, 2*pi)
        move = speed*cos(phi), speed*sin(phi)
        self.x += move[0]
        self.y += move[1]
        return move

    def __repr__(self):
        return "<%s at %s x: %f, y: %f>" % (self.__class__.__name__, id(self), self.x, self.y)
    
    def sense(self):
        if self.t_remaining < params.t_sense:
            raise Exception('No time remained for sensing')
        self.t_remaining -= params.t_sense
        self.E_slot += params.P_sense * params.t_sense
        return self.env.detect_traffic(self.chan)
    
    def switch(self, chan):
        if self.t_remaining < params.t_sw * abs(chan - self.chan):
            raise Exception('No time remained for switching from chan #%d to chan #%d' % (self.chan, chan))
        self.E_slot += abs(chan - self.chan) * params.t_sw * params.P_sw
        self.t_remaining -= params.t_sw * abs(chan - self.chan)   
        self.chan = chan
    
    def transmit(self, P_tx, n_pkg):
        self.n_pkg_slot = n_pkg
        n_bits = n_pkg * params.pkg_size
        if self.t_remaining < n_bits / params.bitrate:
            raise Exception('No time remained for transmitting %d bits with bitrate %f' % (n_bits, bitrate))
        self.t_remaining -= n_bits / params.bitrate
        self.E_slot += P_tx * n_bits / params.bitrate
        return {
            'action': 'transmit',
            'channel': self.chan,
            'power': P_tx,
            'pkt_size': params.pkg_size,
            'n_pkt': n_pkg,
            'bitrate': params.bitrate
        }
    
    def idle(self):
        self.E_slot += params.P_idle * self.t_remaining
        self.t_remaining = 0
        return {
            'action': 'idle'        
        }
        
    def feedback(self, collision, success, idle=False):
        if idle:
            return
        if success:
            self.B_empty += 1
        if self.B_empty > self.B:
            self.B_empty = self.B
    
    def act_then_idle(self):
        a = self.act()
        self.idle()
        return a
    
    def calculate_bitrate(self, P_tx, ch):
        return params.chan_bw * log2(1 + P_tx / self.env.channels[ch].noise())