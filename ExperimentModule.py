# -*- coding: utf-8 -*-
"""
Created on Fri May 16 11:49:04 2014
@author: Seyed Iman Mirzaei

Experiment control module.
"""
EXP_module_version = '1.0.0'
print('Experiment module version: ',EXP_module_version)

import DataModule as d_m
import E5071C as vna_m
import APSIN20G as sig_m





def VNA_read(fstart,fstop,power=-60,wait=60):
    x, y = vna_m.collect_sparam(fstart,fstop,power,wait)  
        
    dat = d_m.data_2d()
    dat.load_var(x,y)
    
    return dat

