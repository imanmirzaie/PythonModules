# -*- coding: utf-8 -*-
"""
Created on Thu Apr 10 17:03:53 2014

@author: Seyed Iman Mirzaei
Version 1.1.0
"""

DataModule_module_version = '1.1.0'

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import scipy.stats as stat
import pickle
from scipy import optimize,signal,interpolate

##############################################################################
# Functions
##############################################################################
def plot_temp_2col(fontname='Arial'):
    ''' This function generates a plot template for publication in 2-column papers. After calling this function
    one needs to populate the graph with data using ordinary plotting commands.
    example: 
    
    import DataModule as dm
    import matplotlib.pyplot as plt
    dm.plot_temp_2col()
    plt.plot(x,y)
    '''
    
    fig, ax = plt.subplots()

    # figure properties
    fig.set_size_inches((12,9))

    # axes (not axis) properties

    # axes title
    #ax.set_title('Axes title')
    ax.title.set_position((0.5,1.02))
    ax.title.set_fontsize(26)
    ax.title.set_fontname('Times New Roman')

    # axis properties
    for sp in ax.spines.values(): # spine properties
        sp.set_linewidth(2)
    
    # axis ticks and tick labels
    ax.tick_params(axis='both', length=6, width=2, pad=10)
    tickfonts = matplotlib.font_manager.FontProperties(family=fontname,size=24)
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontproperties(tickfonts)
    
    ax.xaxis.get_major_formatter().set_useOffset(False)
    ax.yaxis.get_major_formatter().set_useOffset(False)
    
    # axis labels
    labelfontdict = {'fontname':fontname,'fontsize':26}
    ax.xaxis.set_label_text('x-axis label',fontdict=labelfontdict)
    ax.xaxis.labelpad = 20
    
    ax.yaxis.set_label_text('y-axis label',fontdict=labelfontdict)
    ax.yaxis.labelpad = 20
    
    return fig,ax


def cleandat(x,y):
    """
    This function takes a two row data matrix (x,y) and does the following:
    1- sorts the data in ascending form based on the x row.
    2- finds the unique values of x and put the average of corresponding y in the y column
    in the future: 3- adds a third row with standard deviation for multiple data (indication of statistical error)
    """
    # check data form
    
    # assign variables
    #x = dat[1,:]
    #y = dat[2,:]
    
    x_sort_idx = np.argsort(x)
    x_srt = x[x_sort_idx]
    y_srt = y[x_sort_idx]
    
    # finding unique values
    x_uq,x_uq_idx = np.unique(x_srt,return_index=True)
    
    # the statistic loop
    l = len(x_uq_idx)
    y_out = np.ones(l)
    y_err = np.ones(l)
    

    for i in np.arange(l-1):
        y_out[i] = np.mean(y_srt[x_uq_idx[i]:x_uq_idx[i+1]])
        #y_err[i] = np.std(y_srt[x_uq_idx[i]:x_uq_idx[i+1]])
        y_err[i] = stat.sem(y_srt[x_uq_idx[i]:x_uq_idx[i+1]])
    
    y_out[-1] = np.mean(y_srt[x_uq_idx[-1]:])
    #y_err[-1] = np.std(y_srt[x_uq_idx[-1]:])
    y_err[-1] = stat.sem(y_srt[x_uq_idx[-1]:])
    
    return x_uq, y_out, y_err


def parity(number):
    if (number & 1):
        print("Odd!")
    else:
        print("Even!")


def split(vector,range_vector):
    """This function gets a list (array) of ranges (must have even members) and returns 
    the data in x that fall within those ranges.  """
    
    # Convert input to row vectors
    x = np.array(vector).ravel()
    ranges = np.array(range_vector).ravel()
    
    # initialize variables
    idx = np.ma.zeros(len(x)) 
    
    # check if "ranges" has even elements
    if (len(range_vector) & 1):
        raise Exception('Number of range elements must be even.')
    else:
        # Making the new index and output
        for i in range(int(len(ranges)/2)):
            idx_tmp = np.logical_and(x>=ranges[2*i],x<=ranges[2*i+1])
            idx = np.logical_or(idx,idx_tmp)
        return idx,vector[idx]

def smooth(x,y,nnb):
    """This is a very simple smoothing function that for each point in x, takes
    the average value of corresponding y and its 'nnb' neighbors on each side.
    WARNING: the 'nnb' points at the beginning and the end should be handled with care as
    they are averaged on a non-symmetric window.    
    
    This example takes average on a 21-point window.(10 on each side and the point itself)
    y_smth = smooth(x,y,10)  """
    def lo_lim(i):
        return i if i > 0 else 0
    def hi_lim(i):
        return i+1 if i < len(x)-1 else len(x)
    
    yy = np.zeros(np.shape(y))
    
    for i in np.arange(len(x)):
        msk = np.arange(lo_lim(i-nnb),hi_lim(i+nnb))
        yy[i] = np.mean(y[msk])
    
    return yy
        

    
def smooth_vec(x,y,nnb):
    """This is a very simple smoothing function that for each point in x, takes
    the average value of corresponding y and its 'nnb' neighbors on each side.
    WARNING: the 'nnb' points at the beginning and the end should be handled with care as
    they are averaged on a non-symmetric window.    
    
    This example takes average on a 21-point window.(10 on each side and the point itself)
    y_smth = smooth(x,y,10)  """
    def lo_lim(i):
        return i if i > 0 else 0
    def hi_lim(i):
        return i+1 if i < len(x)-1 else len(x)
    
    yy = np.zeros(np.shape(y))
    
    for i in np.arange(len(x)):
        msk = np.arange(lo_lim(i-nnb),hi_lim(i+nnb))
        yy[:,i] = np.mean(y[:,msk],axis=1)
    
    return yy
	
##############################################################################
# Classes        
##############################################################################

class data_2d(object):
    def __init__(self):
        self.x = []
        self.y = []
        
        self.comments = ''
        
        self.xsel = []
        self.ysel = []
    
    def load(self,fname):
        self.dat = np.genfromtxt(fname)
        self.x = self.dat[:,0]
        self.y = self.dat[:,1]
        self.select()
        #self.x = np.reshape(self.dat[:,0],-1)
        #self.y = np.reshape(self.dat[:,1],-1)

    def load_var(self,x,y):
        self.x = x
        self.y = y
        self.select()
        
    def save(self,fname):
        dat_sav = np.hstack((self.xsel[:,None],self.ysel[:,None]))
        np.savetxt(fname,dat_sav) 
        
    def save_OBJ(self,fname):
        with open(fname, "wb") as f:
            pickle.dump(self, f)

    def select(self,xrng = [0,0]):
        x_rng = []
        
        if  xrng == [0,0]:
            x_rng = [self.x[0],self.x[-1]]
        else:
            x_rng = xrng
                        
        xsel_idx,self.xsel = split(self.x,x_rng)
        self.ysel = self.y[xsel_idx]

        
    def plot(self,figure_size=(16,9),xlab = 'X', ylab = 'Y' ):
        plt.figure(figsize=figure_size)
        plt.xlabel(xlab,fontsize=14)
        plt.ylabel(ylab,fontsize=14)
        plt.plot(self.xsel,self.ysel)
        plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)
        plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)
    
    def fit(self,fitfunc1,fit1_p_init,plot=True,plot_init=True,figuresize=(16,9)):
        
        errfunc1 = lambda p, x: fitfunc1(p, x) - self.ysel # Distance to the target function
        fit1_p_fit, success1 = optimize.leastsq(errfunc1, fit1_p_init[:], args=(self.xsel))
        
        if plot is True:
            plt.figure(figsize=figuresize)
            if plot_init is True:
                plt.plot(self.xsel, self.ysel, "bo", self.xsel, fitfunc1(fit1_p_init, self.xsel), "g-", self.xsel, fitfunc1(fit1_p_fit, self.xsel), "r-",linewidth=2) # Plot of the data and the fit
                plt.legend(('Data', 'Init', 'fit'))
            else:
                plt.plot(self.xsel, self.ysel, "bo", self.xsel, fitfunc1(fit1_p_fit, self.xsel), "r-",linewidth=2) # Plot of the data and the fit
                plt.legend(('Data', 'fit'))
            plt.title("Fitting to a given function",fontsize=20)
            plt.xlabel("X",fontsize=14)
            plt.ylabel("Y",fontsize=14)
            plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)
            plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)

        #ax = plt.axes()
        #plt.text(0.2, 0.4,
        #     '$Q_{ext}$ =  %.3f \n $Q_{tot}$ = %.3f \n $Q_{int}$ = %.3f \n $\delta f$ = %.3f \n $f_r$ = %.3f \n Offset = %.3f' %(fit1_p_fit[0],fit1_p_fit[1],qint,fit1_p_fit[2],fit1_p_fit[3],fit1_p_fit[4]),
        #     fontsize=16,
        #     horizontalalignment='center',
        #     verticalalignment='center',
        #     transform=ax.transAxes)
        return fit1_p_fit, np.sum(errfunc1(fit1_p_fit,self.xsel)**2)
        
    def localmin(self,min_threshold, npoints =1):
        msk = self.ysel < min_threshold
        xx = self.xsel[msk]        
        yy = self.ysel[msk]        
        min_idx = signal.argrelextrema(yy, np.less, order = npoints)
        return np.vstack((np.frombuffer(xx[min_idx]),np.frombuffer(yy[min_idx])))
    
    def smooth(self,nnb):
        self.ysel = smooth(self.xsel,self.ysel,nnb)
        
    def interp(self,xnew):
        ''' This method interpolates the data to the new x and y coordinates.
        Example (assuming "d2" object contains our data): 
        
        xnew = linspace(d2.x.min(),d2.x.max(),100)
        d2.interp(xnew)
        d2.plot()      '''
        f = interpolate.interp1d(self.xsel, self.ysel)
        self.xsel = xnew
        self.ysel = f(xnew)
        

##############################################################################
class data_3d(object):
    def __init__(self):
        self.x = []
        self.y = []
        self.z = []
        
        self.comments = ''
        
        self.xsel = []
        self.ysel = []
        self.zsel = []
    
    
    def load(self,fname,x=None,y=None):
        self.dat = np.genfromtxt(fname)
        if x == None and y == None:
            self.x = self.dat[0,1:]
            self.y = self.dat[1:,0]
            self.z = self.dat[1:,1:]
            
            self.xsel = self.dat[0,1:]
            self.ysel = self.dat[1:,0]
            self.zsel = self.dat[1:,1:]
            
        elif x != None and y != None:
            self.x = x
            self.y = y
            self.z = self.dat
            
            self.xsel = x
            self.ysel = y
            self.zsel = self.dat
            
        elif x == None and y != None:
            self.x = self.dat[0,:]
            self.y = y
            self.z = self.dat[1:,:]
            
            self.xsel = self.dat[0,:]
            self.ysel = y
            self.zsel = self.dat[1:,:]
            
        elif x != None and y == None:
            self.x = x
            self.y = self.dat[:,0]
            self.z = self.dat[:,1:]
            
            self.xsel = x
            self.ysel = self.dat[:,0]
            self.zsel = self.dat[:,1:]


    def load_var(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z
        self.select()

    
    def save(self,fname,x=None,y=None):
        if x == None and y == None:
            dat_sav = np.hstack((np.vstack((0,self.ysel[:,None])),np.vstack((self.xsel,self.zsel))))
            np.savetxt(fname,dat_sav)
        elif x != None and y != None:
            #
            x=0
        elif x == None and y != None:
            #
            x=0
        elif x != None and y == None:
            #
            x=0

    
    def save_OBJ(self,fname):
        with open(fname, "wb") as f:
            pickle.dump(self, f)        

    
    def imshow(self,figure_size=(16,9),colormap = plt.cm.hsv, lev = 'Default',xlab = 'X', ylab = 'Y', norm = 'Default'):
        plt.figure(figsize=figure_size)
        
        if lev == 'Default':
            levels = np.linspace(self.zsel.min(),self.zsel.max(), 10) 
        else:
            levels = lev
            
        if norm == 'Default':
            normal = plt.cm.colors.Normalize(vmax=abs(self.zsel).max(), vmin=-abs(self.zsel).max())
        else:
            normal = norm
            
        
        #norm = plt.cm.colors.Normalize(vmax=self.zsel.max(), vmin=-abs(self.zsel).max())
        cmap = colormap
        plt.xlabel(xlab,fontsize=18)
        plt.ylabel(ylab,fontsize=18)
        plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)
        plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)
        ax = plt.subplot()
        for item in (ax.get_xticklabels() + ax.get_yticklabels()):
            item.set_fontsize(14)
        plt.imshow(self.zsel,
                    cmap=plt.cm.get_cmap(cmap, len(levels)-1),
                    norm=normal,
                    interpolation=None,
                    aspect='auto',
                    extent=[self.xsel.min(),
                            self.xsel.max(),
                            self.ysel.min(),
                            self.ysel.max()])
        plt.colorbar()
        
    def contourf(self,figure_size=(16,9),colormap = plt.cm.hsv, lev = 'Default',xlab = 'X', ylab = 'Y', norm = 'Default'):
        plt.figure(figsize=figure_size)
        
        if lev == 'Default':
            levels = np.linspace(self.zsel.min(),self.zsel.max(), 10) 
        else:
            levels = lev
            
        if norm == 'Default':
            normal = plt.cm.colors.Normalize(vmax=abs(self.zsel).max(), vmin=-abs(self.zsel).max())
        else:
            normal = norm
            
        
        #norm = plt.cm.colors.Normalize(vmax=self.zsel.max(), vmin=-abs(self.zsel).max())
        cmap = colormap
        plt.xlabel(xlab,fontsize=18)
        plt.ylabel(ylab,fontsize=18)
        plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)
        plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)
        ax = plt.subplot()
        for item in (ax.get_xticklabels() + ax.get_yticklabels()):
            item.set_fontsize(14)
        plt.contourf(self.xsel,self.ysel,self.zsel,levels,cmap=plt.cm.get_cmap(cmap, len(levels)-1),norm=normal,)
        plt.colorbar()
        
        
    def select(self,xrng=[0,0],yrng=[0,0]):
        x_rng = []
        y_rng = []
        
        if  xrng == [0,0]:
            x_rng = [self.x[0],self.x[-1]]
        else:
            x_rng = xrng
                    
        if yrng == [0,0]:
            y_rng = [self.y[0],self.y[-1]]
        else:
            y_rng = yrng
        
        xsel_idx,self.xsel = split(self.x,x_rng)
        ysel_idx,self.ysel = split(self.y,y_rng)
        #
        #self.zsel = self.z[ysel_idx,:] ; self.zsel = self.zsel[:,xsel_idx]
        zsel_tmp = self.z[ysel_idx,:]
        self.zsel = zsel_tmp[:,xsel_idx]
        
    def smoothx(self,nnb):
        return smooth_vec(self.xsel,self.zsel,nnb)

    def smoothy(self,nnb):
        return smooth_vec(self.ysel,self.zsel.transpose(),nnb).transpose()

    def interp(self,xnew,ynew):
        ''' This method interpolates the data to the new x and y coordinates.
        Example (assuming "d3" object contains our data): 
        
        xnew = linspace(d2.x.min(),d2.x.max(),100)
        ynew = linspace(d2.y.min(),d2.y.max(),100)
        d3.interp(xnew,ynew)
        d3.contourf()        
        
        '''
        f = interpolate.interp2d(self.xsel, self.ysel, self.zsel, kind='cubic')
        self.xsel = xnew
        self.ysel = ynew
        self.zsel = f(xnew,ynew)
        
        