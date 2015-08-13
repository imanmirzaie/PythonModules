# -*- coding: utf-8 -*-
"""
Created on Fri Mar 28 09:43:05 2014

@author: Seyed Iman Mirzaei

Module for communicating with ENA E5071C and analysing data
"""
E5071C_module_version = '2.0.0'
print('E5071C module version: ',E5071C_module_version)

import vxi11 as vx
import DataModule as dm
import time
import numpy as np

###############################################################################################
# Constants
def_ip = '192.168.0.103'

###############################################################################################
class VNA(object):
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
    
    def query_only(self,str1,arg='?'):
        if arg == '?':
            return (self.query(str1))
        else:
            raise ValueError('No arguments allowed. This is only a query.')
        
    def cmd_query(self,str1,arg='?'):
        if arg == '?':
            return self.query(str1)
        else:
            self.cmd(str1,arg)
    
    # Close connection
    def close(self):
        self.v.close()
    
    
    # Identification
    def identify(self):
        str1 = '*OPT'
        return self.query(str1)
        
    def output(self,arg='?'): # arg = ON|OFF|1|0
        """ Turns RF output power on/off."""
        str1 = ':OUTPut'
        return self.cmd_query(str1,arg)
        
        
    #POWER settings
    def power(self,power='?',channel=''):
        str1 = ''.join([':SOURce',str(channel),':POWer:LEVel:IMMediate:AMPLitude'])
        return self.cmd_query(str1,power)

    
    # AVERAGE settings
    def average_reset(self,channel=''):
        str1 = ''.join([':SENSe',str(channel),':AVERage:CLEar'])
        return self.cmd_only(str1,'')
    
    def average_count(self,count='?',channel=''):
        str1 = ''.join([':SENSe',str(channel),':AVERage:COUNt'])
        return self.cmd_query(str1,count)
        
    def average_state(self,state='?',channel=''):
        str1 = ''.join([':SENSe',str(channel),':AVERage:STATe'])        
        return self.cmd_query(str1,state)
        
    # FREQUENCY sweep setting
    def freq_start(self,freq='?',channel=''):
        str1 = ''.join([':SENSe',str(channel),':FREQuency:STARt'])
        return self.cmd_query(str1,freq)
    
    def freq_stop(self,freq='?',channel=''):
        str1 = ''.join([':SENSe',str(channel),':FREQuency:STOP'])
        return self.cmd_query(str1,freq)
        
    def freq_center(self,freq='?',channel=''):
        str1 = ''.join([':SENSe',str(channel),':FREQuency:CENTer'])
        return self.cmd_query(str1,freq)
            
    def freq_span(self,freq='?',channel=''):
        str1 = ''.join([':SENSe',str(channel),':FREQuency:SPAN'])
        return self.cmd_query(str1,freq)
        
    def freq_npoints(self,points='?',channel=''):
        str1 = ''.join([':SENSe',str(channel),':SWEep:POINts'])
        return self.cmd_query(str1,points)
        
    # READING data
    def freq_read(self):
        str1 = 'CALCulate:TRACe:DATA:XAXis'
        return self.query(str1).split(',')
    
    def trace_read(self,channel=''):
        str1 = ''.join(['CALCulate',str(channel),':TRACe:DATA:FDATa'])
        dat = self.query(str1).split(',')
        return dat[0::2],dat[1::2]
        
    # Setting the IF bandwidth
    # This command sets/gets the IF bandwidth of selected channel (Ch).
    def IFBW(self,BW='?',channel=''):
        str1 = ''.join([':SENSe',str(channel),':BANDwidth:RESolution'])
        return self.cmd_query(str1,BW)
        
    def collect_single(self,f_range,npoints=1601,navg = 999,power=-50,wait=1,BW=1e3):
        '''This function reads S-parameter from the VNA using the specified setting:
        f_range: frequency range in form of a list [f_start, f_stop]
        npoints: the the number of frequency points to measure
        navg = number of averaging measurements (average coefficient)
        power = RF_out power in dB
        wait =  data collection time in seconds
        BW = IF bandwidth'''
        self.IFBW(BW)
        self.freq_npoints(npoints)    
        self.freq_start(f_range[0])
        self.freq_stop(f_range[1])
        self.power(power)
        if (navg==0):
            self.average_state(0)
        else:
            self.average_state(1)
            self.average_count(navg)
            
        self.average_reset()
        time.sleep(wait) # delay
        x = np.asarray(self.freq_read(),dtype='float')
        y = np.asarray(self.trace_read()[0],dtype='float') 
    
        dat = dm.data_2d()  
        dat.load_var(x,y)
        return dat

    def collect_scan(self,f_range_mat,npoints_v=[1601],navg_v = [999],power_v=[-50],wait_v=[1],BW_v=[1e3]):
        x = []
        y = []
        range_mat = np.array(f_range_mat)
        len_loop = len(range_mat[:,0])

        def vector_handling(vector):
            if len(vector) == 1:
                out = vector[0]*np.ones(len_loop)
            else:
                out = vector
            return out            
    
        npoints = vector_handling(npoints_v)
        navg = vector_handling(npoints_v)
        power = vector_handling(power_v)
        wait = vector_handling(wait_v)
        BW = vector_handling(BW_v)
    
        for i in np.arange(len_loop):
            f_range = range_mat[i,:]           
            dat_tmp = self.collect_single(f_range,npoints[i],navg[i],power[i],wait[i],BW[i])   
            x = np.hstack((x,dat_tmp.x))
            y = np.hstack((y,dat_tmp.y)) 
        
        dat = dm.data_2d()  
        dat.load_var(x,y)   
        return dat

    def collect_single_correct(self,f_range,npoints=1601,navg=999,power=-50,corr_power=-10,wait=10,corr_wait=1,BW=1e3):
            dat_cor = self.collect_single(f_range,npoints,navg,corr_power,corr_wait,BW)        
            dat_mes = self.collect_single(f_range,npoints,navg,power,wait,BW)        
        
            dat = dm.data_2d()
            dat.load_var(dat_mes.x,dat_mes.y-dat_cor.y)
            return dat

    def collect_scan_correct(self,f_range_mat,npoints_v=[1601],navg_v = [999],power_v=[-50],corr_power_v=[-10],wait_v=[10],corr_wait_v=[1],BW_v=[1e3]):
            dat_cor = self.collect_scan(f_range_mat,npoints_v,navg_v,corr_power_v,corr_wait_v,BW_v)        
            dat_mes = self.collect_scan(f_range_mat,npoints_v,navg_v,power_v,wait_v,BW_v)        
        
            dat = dm.data_2d()
            dat.load_var(dat_mes.x,dat_mes.y-dat_cor.y)
            return dat
        






