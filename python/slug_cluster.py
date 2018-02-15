#!/usr/bin/env python

import os
import time
import numpy as np
from collections import namedtuple

from scipy import integrate
from astropy import units as au
from astropy import constants as ac
import cPickle as pickle

# slugpy should be added to the PYTHONPATH environment variable
from slugpy import read_cluster_spec,read_cluster_phot,read_cluster_prop

class slug_cluster(object):
    """Data analysis routines for SLUG2 cluster simulation spec output

    calculate integrated lumionosity, photon output rate, mean energy of
    photons in specified bands.
    """
    def __init__(self,output_dir='/media/jgkim/data2/output_slug2',
                 model_base='cluster_logM',fmt='bin'):

        ## simulation and output parameters
        self.logM_all = np.linspace(2.0,3.0,6)
        self.proc_all = range(5)              # number of threads (p0001...p000x)
        self.output_dir = output_dir
        
        self.model_base = model_base
        self.fmt = fmt
        
        # physical units and constants
        self.Angs = (1.0*au.Angstrom).cgs.value
        self.hc = (1.0*(ac.h*ac.c).cgs).value
        self.L_sun = (1.0*au.L_sun).cgs.value

        # bands
        self.wl_lim = {'H0': (0.0,912.11), # Lyman edge
                       'FUV': (912.11,(ac.h*ac.c/(6.0*au.eV)).to('Angstrom').value), # 2066 A
                       'LW': (912.11,1108.0) # LW band (~ 11.3 - 13.6 eV) ref. Sternberg+14
                      }
        self.bands = self.wl_lim.keys()
        self.wl_lim_indx = dict()

        # pickle directory
        self.pkl_dir = os.path.join(output_dir,'pickle')
        if not os.path.exists(self.pkl_dir):
            os.makedirs(self.pkl_dir)
           
    def read_cluster(self,logM=None,proc=None,verbose=False):
        """
        Read one set of output files for given logM and proc
        """

        self.set_logM_proc(logM,proc)
        if verbose:
            time0=time.time()
        self.spec=read_cluster_spec(self.model_name,output_dir=self.output_dir,fmt=self.fmt)
        self.phot=read_cluster_phot(self.model_name,output_dir=self.output_dir,fmt=self.fmt)
        self.prop=read_cluster_prop(self.model_name,output_dir=self.output_dir,fmt=self.fmt)
        if verbose:
            print '[read_cluster]: {:.2f} s'.format(time.time()-time0)

        self.target_mass=self.prop.target_mass[0]
        self.trials=np.unique(self.phot.trial)
        self.ntrial=len(self.trials)
        self.ntime=np.argwhere(self.phot.trial == 1).shape[0]
        self.time=self.phot.time[0:self.ntime]
        self.wl=self.spec.wl

        ## Find band edge indices
        ## 1. band edges are not carefully taken care of.
        ## 2. wavelength resolution is not very good.
        ## Hence the resulting integration may not be very accurate,
        ## but it should be good enough for our purposes.
        for k,(wl1,wl2) in self.wl_lim.items():
            self.wl_lim_indx[k] = (np.argwhere(self.wl > wl1)[0][0],
                                   np.argwhere(self.wl < wl2)[-1][0]+1)

    def set_logM_proc(self,logM=None,proc=None):
        if logM is not None:
            self.logM = logM
        if proc is not None:
            self.proc = proc
        self.model_name = self.model_base + \
          '{0:02d}_p{1:05d}_n00000_0000'.format(int(10.0*self.logM),self.proc)

    def set_trial(self,trial):
        """
        1 <=  trial <= ntrial 
        """
        
        # index range of this trial
        ii = int((trial-1)*self.ntime)
        ie = int((trial)*self.ntime)
        self.phot_ = self.phot.phot[ii:ie,:]
        self.spec_ = self.spec.spec[ii:ie,:]

    def integrate_spec(self,logM,force_override=False,verbose=False):

        if verbose:
            print "[integrate_spec]: logM ",logM

        fpkl = os.path.join(self.pkl_dir,self.model_base + "{0:02d}.p".format(int(10.0*logM)))
        print fpkl
        # Check if pickle exists
        if not force_override and os.path.isfile(fpkl):
            self.out = pickle.load(open(fpkl,'rb'))
            for k in self.out.keys():
                setattr(self,k,self.out[k])
            print "[integrate_spec]: read from pickle {0:s}".format(fpkl)
            return self.out
        else:
            print "[integrate_spec]: {0:s} does not exist. Read SLUG2 output and integrate...".format(fpkl)

            
        # pickle does not exists

        append=False
        #for proc in (0,): # for test
        for proc in self.proc_all:
            print 'proc',proc
            self.set_logM_proc(logM,proc)
            self.read_cluster(verbose=verbose)
            self.integrate_spec_trials(integrate_method='trapz',
                                       append=append,verbose=verbose)
            append=True

        # calculate total number of trials
        self.ntrial_tot = self.L[self.bands[0]].shape[0]

        # compute median values
        self.L_med = dict()
        self.Q_med = dict()
        self.Psi_med = dict()
        self.Xi_med = dict()
        self.hnu_med = dict()

        self.Lbol_med = np.median(self.Lbol,axis=0)
        self.Psibol_med = np.median(self.Lbol,axis=0)
        
        for k in self.bands:
            self.L_med[k] = np.median(self.L[k],axis=0)
            self.Q_med[k] = np.median(self.Q[k],axis=0)
            self.hnu_med[k] = np.median(self.hnu[k],axis=0)
            
            self.Psi_med[k] = self.L_med[k]/self.target_mass
            self.Xi_med[k] = self.Q_med[k]/self.target_mass
            
            
        # Build dictionary to hold output
        keys = ['ntrial_tot', 'time', 'bands', 'target_mass', 'ntime',
                'Lbol', 'L', 'Q', 'hnu',
                'Lbol_med','L_med','Q_med','hnu_med',
                'Psibol_med', 'Psi_med', 'Xi_med']

        out = dict()
        for k in keys:
            out[k] = getattr(self,k)
        
        with open(fpkl,'wb') as f:
            pickle.dump(out,f,pickle.HIGHEST_PROTOCOL)

        return out
        
    def integrate_spec_trials(self,integrate_method='trapz',
                              append=False,verbose=False):

        if not append:
            self.Lbol = dict()
            self.L = dict()
            self.Q = dict()
            self.hnu = dict()

        if verbose:
            print 'ntrial:',self.ntrial
            print 'trials:',
            
        #for i,ii in enumerate((1,2,3,5,6,7,8,9,10)): # for test 
        for i,ii in enumerate(self.trials):
            if verbose:
                print ii,

            self.set_trial(ii)
            self.integrate_spec_one_trial(integrate_method=integrate_method)
            
            # save results to L,Q,hnu
            if i == 0 and not append:
                self.Lbol = self.Lbol_
            else:
                self.Lbol = np.vstack((self.Lbol,self.Lbol_))
            for k in self.bands:
                if i == 0 and not append:
                    self.L[k] = self.L_[k]
                    self.Q[k] = self.Q_[k]
                    self.hnu[k] = self.hnu_[k]
                else:
                    self.L[k] = np.vstack((self.L[k],self.L_[k]))
                    self.Q[k] = np.vstack((self.Q[k],self.Q_[k]))
                    self.hnu[k] = np.vstack((self.hnu[k],self.hnu_[k]))

        if verbose:
            print ""
            print ""

    def integrate_spec_one_trial(self,integrate_method='trapz'):
        """Analyze spec with one trial
        integrate_method: 'trapz' or 'simps'
        """

        integrators = {'trapz': integrate.trapz,
                       'simps': integrate.simps}
        integrator = integrators[integrate_method]

        self.Lbol_ = np.zeros(self.ntime)
        
        self.L_ = dict()
        self.Q_ = dict()
        self.hnu_ = dict()
        for k in self.bands:
            self.L_[k] = np.zeros(self.ntime)
            self.Q_[k] = np.zeros(self.ntime)

        # loop over time
        wl=self.wl
        for j in range(self.ntime):
            s = self.spec_[j,:]
            # Bolometric
            self.Lbol_[j] = integrator(s,wl)/self.L_sun

            # band L, Q
            for k in self.bands:
                s_  =  s[self.wl_lim_indx[k][0]:self.wl_lim_indx[k][1]+1]
                wl_ = wl[self.wl_lim_indx[k][0]:self.wl_lim_indx[k][1]+1]

                self.L_[k][j] = integrator(s_,wl_)/self.L_sun
                self.Q_[k][j] = integrator(s_*wl_/self.hc,wl_)*self.Angs

        # mean photon energy
        for k in self.bands:
            self.hnu_[k] = ((self.L_[k]*au.L_sun)/(self.Q_[k]/au.s)).to('eV').value


if __name__ == '__main__':

    # read all output, integrate, and pickle
    force_override=True
    sc = slug_cluster()
    for logM in sc.logM_all:
        print '[main]: logM',logM
        sc = slug_cluster()
        sc.integrate_spec(logM=logM,force_override=force_override,verbose=True)

