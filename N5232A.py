# -*- coding: utf-8 -*-
"""
Created on Fri Mar 28 09:43:05 2014

@author: Seyed Iman Mirzaei

Module for communicating with ENA N5232A and analysing data
"""
N5232A_module_version = '1.0.0'
print('N5232A module version: ',N5232A_module_version)

#import vxi11 as vx
import socket
import DataModule as dm
import time
import numpy as np




###############################################################################################
# Constants
def_ip = '192.168.0.134'
def_port = 5025
###############################################################################################


class VNA(object):
    def __init__(self,ip = def_ip, port = def_port):
        #self.v = vx.Instrument(str(ip))
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.connect((ip, port))
        except socket.error as e:
            print("socket error")    
    
    def recv_timeout(self,timeout=2):
        #make socket non blocking
        the_socket=self.s
        the_socket.setblocking(0)
         
        #total data partwise in an array
        total_data=[];
        data='';
         
        #beginning time
        begin=time.time()
        while 1:
            #if you got some data, then break after timeout
            if total_data and time.time()-begin > timeout:
                break
             
            #if you got no data at all, wait a little longer, twice the timeout
            elif time.time()-begin > timeout*2:
                break
             
            #recv something
            try:
                data = the_socket.recv(8192)
                if data:
                    total_data.append(str(data)[2:-1])
                    #change the beginning time for measurement
                    begin=time.time()
                else:
                    #sleep for sometime to indicate a gap
                    time.sleep(0.1)
            except:
                pass
         
        #join all parts to make final string
        return ''.join(total_data)[:-2]
#    def read(self,msg):
#        self.s.send(''.join([msg,'\n']).encode('UTF-8'))
#        #return self.s.recv(1024).split(':')[-1][:-1]
#        return self.s.recv(1024)
    
    def cmd(self,str1,arg):
        self.s.send(''.join([str(str1),' ',str(arg),'\n']).encode('UTF-8'))
        #return self.s.recv(1024)

    def query(self,str1,timeout=0.5):
        self.s.send(''.join([str(str1),'?','\n']).encode('UTF-8'))
        return self.recv_timeout(timeout)
        
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
        self.s.close()
    
    
    # Identification
    def identify(self):
        str1 = '*IDN'
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
    
    def average_completed(self,channel=1):
        cmd1='STAT:OPER:AVER'+str(channel)+':COND'
        register = bin(int(self.query(cmd1)))
        
        if len(register)<3:
            return False
        else:
            if register[2]=='0':
                return False
            else: 
                return True
        
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
    def freq_read(self,MeasName):
        str1 = 'CALC:PAR:SEL'
        str2 = 'CALC:X'
        self.cmd(str1,'\''+MeasName+'\'')
        return self.query(str2).split(',')
    
    def trace_read(self):
        #str1 = ''.join(['CALCulate',str(channel),':TRACe:DATA:FDATa'])
        str1 = ''.join(['CALC:DATA? FDATA'])
        self.cmd(str1,'')
        return self.recv_timeout(0.5).split(',')
        
        
    # Setting the IF bandwidth
    # This command sets/gets the IF bandwidth of selected channel (Ch).
    def IFBW(self,BW='?',channel=''):
        str1 = ''.join([':SENSe',str(channel),':BANDwidth:RESolution'])
        return self.cmd_query(str1,BW)
        
    def collect_single(self,f_range,Name,Trace=1,Spar='S21',npoints=1601,navg = 999,power=-50,wait=1,BW=1e3):
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
        
        self.cmd('CALC'+str(Trace)+':PAR:EXT','\''+Name+'\', \''+Spar+'\'')        
        
        x = np.array(self.freq_read(Name),dtype='float')
        y = np.asarray(self.trace_read(),dtype='float') 
    
        dat = dm.data_2d()  
        dat.load_var(x,y)
        return dat

    def collect_single_ave(self,f_range,Name,Trace=1,Spar='S21',npoints=1601,navg = 100,power=-50,BW=1e3):
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
        
        while(self.average_completed() == False):
            time.sleep(1)
        
        self.cmd('CALC'+str(Trace)+':PAR:EXT','\''+Name+'\', \''+Spar+'\'')        
        
        x = np.array(self.freq_read(Name),dtype='float')
        y = np.asarray(self.trace_read(),dtype='float') 
    
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

    def collect_single_correct(self,f_range,name,npoints=1601,navg=999,power=-50,corr_power=-10,wait=10,corr_wait=1,BW=1e3):
            dat_cor = self.collect_single(f_range,name,npoints=npoints,navg=999,power=corr_power,wait=corr_wait,BW=1e3)   
            self.power(-70)            
            time.sleep(2)
            dat_mes = self.collect_single(f_range,name,npoints=npoints,navg=navg,power=power,wait=wait,BW=BW)        
        
            dat = dm.data_2d()
            dat.load_var(dat_mes.x,dat_mes.y-dat_cor.y)
            return dat
            
    def collect_single_correct_ave(self,f_range,name,npoints=1601,navg=100,power=-50,corr_power=-10,corr_wait=1,BW=1e3):
            dat_cor = self.collect_single(f_range,name,npoints=npoints,navg=999,power=corr_power,wait=corr_wait,BW=1e3)        
            self.power(-70)            
            time.sleep(2)
            dat_mes = self.collect_single_ave(f_range,name,npoints=npoints,navg=navg,power=power,BW=BW)        
        
            dat = dm.data_2d()
            dat.load_var(dat_mes.x,dat_mes.y-dat_cor.y)
            return dat

    def collect_scan_correct(self,f_range_mat,npoints_v=[1601],navg_v = [999],power_v=[-50],corr_power_v=[-10],wait_v=[10],corr_wait_v=[1],BW_v=[1e3]):
            dat_cor = self.collect_scan(f_range_mat,npoints_v,navg_v,corr_power_v,corr_wait_v,BW_v)        
            
            dat_mes = self.collect_scan(f_range_mat,npoints_v,navg_v,power_v,wait_v,BW_v)        
        
            dat = dm.data_2d()
            dat.load_var(dat_mes.x,dat_mes.y-dat_cor.y)
            return dat
        






