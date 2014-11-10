# -*- coding: utf-8 -*-
"""
Created on Thu Nov  6 17:32:00 2014

@author: akif
"""

from numpy import *

def to_dbm(P_watt):
    return 10 * log10(P_watt) + 30

def to_watt(P_dbm):
    return 10 ** ((P_dbm - 30) / 10)

__all__ = ['to_dbm', 'to_watt']