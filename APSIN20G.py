# -*- coding: utf-8 -*-
"""
Created on Mon Apr 07 16:58:40 2014

@author: Seyed Iman Mirzaei

Version 1.0.1
"""
APSIN20G_module_version = '1.0.1'

###############################################################################################
# imports
import vxi11 as vx
import time
import numpy as np
import scipy as sc
from scipy import optimize,signal
import matplotlib.pylab as plt
###############################################################################################

###############################################################################################
# class definition

class APSIN20G(object):
    def __init__(self,ip):
        self.v = vx.Instrument(str(ip))
        
    def cmd(self,str1,arg):
        self.v.write(''.join([str(str1),' ',str(arg),'\n']))

    def query(self,str1):
        return self.v.ask(''.join([str(str1),'?\n']))
        

    def cmd_only(self,str1,arg):
        if arg == '?':
            raise ValueError('No queries allowed. This is only a command.')
        else:
            self.cmd(str1,arg)
    
    def query_only(self,str1,qmsg='Output = ',arg='?'):
        if arg == '?':
            print(qmsg,self.query(str1))
        else:
            raise ValueError('No arguments allowed. This is only a query.')
        
    def cmd_query(self,str1,qmsg='Output = ',arg='?'):
        if arg == '?':
            print(qmsg,self.query(str1))
        else:
            self.cmd(str1,arg)

    # Close connection
    def close(self):
        self.v.close()
        
        
    # Identification
    
    def identify(self):
        return self.query('*IDN?\n')
    
    # :ABORt subsytem    
         
    def abort(self): # arg = ON|OFF|1|0
        """ This command causes the List or Step sweep in progress to abort. Even if INIT:CONT[:ALL] is set to
        ON, the sweep will not immediately re-initiate."""
        str1 = ':ABORt'
        self.cmd_only(str1,'')

        
    # :INITiate Subsystem
    def initiate(self): # 
        """ Sets trigger to the armed state."""
        str1 = ':INITiate'
        self.cmd_only(str1,'')
    
    def initiate_cont(self,arg): # arg = ON|OFF|1|0
        """ Continuously rearms the trigger system after completion of a triggered sweep."""
        str1 = ':INITiate:CONTinuous'
        self.cmd_only(str1,arg)
    
    
    # OUTPut subsytem    
    def output(self,arg='?'): # arg = ON|OFF|1|0
        """ Turns RF output power on/off."""
        str1 = ':OUTPut'
        qmsg = 'RF out = '
        self.cmd_query(str1,qmsg,arg)
        
    
    def output_blanking(self,arg='?'): # arg = ON|OFF|1|0
        """ ON causes the RF output to be turned off (blanked) during frequency changes. OFF leaves RF output
        turned on (unblanked)."""
        str1 = ':OUTPut:BLANking'
        qmsg = 'Blanking = '
        self.cmd_query(str1,qmsg,arg)
        

    # :FREQuency Subsystem
    def frequency(self,arg='?'): # arg = value
        """ This command sets the signal generator output frequency for the CW frequency mode."""
        str1 = ':FREQuency'
        qmsg = 'CW frequency = '
        self.cmd_query(str1,qmsg,arg)
        
    def frequency_mode(self,arg='?'): # arg = FIX|CW|SWEep|LIST|CHIRp
        """ This command sets the frequency mode of the signal generator to CW, (list) sweep or chirp."""
        str1 = ':FREQuency:MODE'
        qmsg = 'Frequency mode = '
        self.cmd_query(str1,qmsg,arg)
        
    def frequency_start(self,arg='?'): # arg = value
        """ This command sets the first frequency point in a chirp or step sweep."""
        str1 = ':FREQuency:STARt'
        qmsg = 'Start frequency = '
        self.cmd_query(str1,qmsg,arg)
            
    def frequency_stop(self,arg='?'): # arg = value
        """ This command sets the last frequency point in a chirp or step sweep."""
        str1 = ':FREQuency:STOP'
        qmsg = 'Stop frequency = '
        self.cmd_query(str1,qmsg,arg)
    
    def frequency_step(self,arg='?'): # 
        """ This query returns the step sizein Hz for a linear step sweep."""
        str1 = ':FREQuency:STEP'
        qmsg = 'Frequency step = '
        self.query_only(str1,qmsg,arg)
            
    def frequency_stepLog(self,arg='?'): # 
        """ This query returns the step size (step factor) for a logarithmic step sweep."""
        str1 = ':FREQuency:STEP:LOGarithmic'
        qmsg = 'Logarithmic frequency step = '
        self.query_only(str1,qmsg,arg)
    
    
    # :CHIRp Subsystem
    
    def chirp_count(self,arg='?'): # arg = INFinite | <val>
        """ This command specifies the number of repetitions for the chirp. Set to INF for infinite repetitions."""
        str1 = ':CHIRp:COUNt'
        qmsg = 'No. of repetitions in chirp= '
        self.cmd_query(str1,qmsg,arg)
        
    def chirp_time(self,arg='?'): # arg = <val>
        """ Sets the time span for the chirp."""
        str1 = ':CHIRp:TIME'
        qmsg = 'CHIRP time span = '
        self.cmd_query(str1,qmsg,arg)
    
    def chirp_direction(self,arg='?'): # arg = UD|DU|DOWN|UP
        """ This command sets the direction of the chirp. DU means direction down first, then direction up. UD
        means direction UP first."""
        str1 = ':CHIRp:DIRection'
        qmsg = 'CHIRP sweep direction = '
        self.cmd_query(str1,qmsg,arg)
        

    # :PHASe Subsystem        



    # :POWer Subsystem
    def power(self,arg='?'): # arg = UD|DU|DOWN|UP
        """ This command sets the RF output power."""
        str1 = ':POWer'
        qmsg = 'Output power = '
        self.cmd_query(str1,qmsg,arg)
    

        
        
    
    
###############################################################################################    
    
###############################################################################################
# Constants
def_ip = '192.168.0.102'
#def_instr = APSIN20G(def_ip)
###############################################################################################
