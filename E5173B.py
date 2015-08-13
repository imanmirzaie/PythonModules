# -*- coding: utf-8 -*-
"""
Created on Fri May 30 18:22:08 2014

@author: Seyed Iman Mirzaei
"""


E5173B_module_version = '1.0.0'

###############################################################################################
# imports
import vxi11 as vx
import time
import numpy as np
import scipy as sc
from scipy import optimize,signal
###############################################################################################

###############################################################################################
# class definition

class E5173B(object):
    def __init__(self,ip):
        self.v = vx.Instrument(str(ip))
        
    def cmd(self,str1,arg):
        self.v.write(''.join([str(str1),' ',str(arg),'\n']))

    def query(self,str1):
        return self.v.ask(''.join([str(str1),'?\n']))
        

    def cmd1(self,str1,arg):
        if arg == '?':
            raise ValueError('No queries allowed. This is only a command.')
        else:
            self.cmd(str1,arg)
    
    def query1(self,str1,qmsg='Output = ',arg='?'):
        if arg == '?':
            print(qmsg,self.query(str1))
        else:
            raise ValueError('No arguments allowed. This is only a query.')
        
    def cmd_query(self,str1,qmsg='Output = ',arg='?'):
        if arg == '?':
            print(qmsg,self.query(str1))
        else:
            self.cmd(str1,arg)
###############################################################################################    
    # Close connection
    def close(self):
        self.v.close()
        
    # Identification    
    def identify(self):
        return self.query('*IDN')
    
    # :FREQuency Subsystem
    def frequency(self,arg='?'): # arg = value
        """ This command sets the signal generator output frequency."""
        str1 = ':FREQuency'
        qmsg = 'CW frequency = '
        self.cmd_query(str1,qmsg,arg)
   
    def frequency_mode(self,arg='?'): # arg = FIX|CW|LIST
        """ This command sets the frequency mode of the signal generator to CW or swept."""
        str1 = ':FREQuency:MODE'
        qmsg = 'Frequency mode = '
        self.cmd_query(str1,qmsg,arg)
        
    # :POWer Subsystem
    def power(self,arg='?'): # arg = power
        """ This command sets the RF output power."""
        str1 = ':POWer'
        qmsg = 'Output power = '
        self.cmd_query(str1,qmsg,arg)
        
    def power_mode(self,arg='?'): # arg = FIXed|LIST
        """ This command sets the signal generator power mode to fixed or swept."""
        str1 = ':POWer:MODE'
        qmsg = 'Power mode = '
        self.cmd_query(str1,qmsg,arg)
    
    # OUTPut subsytem    
    def output(self,arg='?'): # arg = ON|OFF|1|0
        """ Turns RF output power on/off."""
        str1 = ':OUTPut'
        qmsg = 'RF out = '
        self.cmd_query(str1,qmsg,arg)
        
###############################################################################################    
    
###############################################################################################
# Constants
def_ip = '192.168.0.107'
def_instr = E5173B(def_ip)
###############################################################################################
