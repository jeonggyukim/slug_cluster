#!/usr/bin/env python

import sys
import os
import re
import warnings

import numpy as np
import fileinput

def substitute_params(fin,fout,subs):
    # Read templates
    with open(fin, 'r') as f:
        ftemp = f.read()

    # Make substitutions
    for key,val in subs.items():
        ftemp = re.sub(r'@{0}@'.format(key), val, ftemp)

    # Write output files
    with open(fout, 'w') as f:
        f.write(ftemp)

def main():
    """Generate SLUG param files from template. 
    Specify model name, ntrial, etc.
    This script is not error-proof. Use with caution!
    """
    
    # Set model name, log10(initial cluster mass), number of trials
    fname_def = "./param.template"
    model_name_base = "cluster_logM"
    out_dir = '/media/jgkim/data2/output_slug3'
    if os.path.exists(out_dir):
        warnings.warn("out_dir {0:s} already exists.".format(out_dir))
    else:
        os.makedirs(out_dir)
    
    logM = np.linspace(2.0,5.0,num=16)
    ntrial = 1000
    n_trials = np.repeat(ntrial,logM.size)

    # Create strings for substitution.
    # See template.cluster.param for more details.
    subs={}
    subs['out_dir'] = '/media/jgkim/data2/output_slug3'
    subs['time_step'] = 1e5        # Starting time (in yr) (default start_time = time_step)
    subs['end_time'] = 40.1e6      # Maximum evolution time, in yr.
    
    subs['out_cluster'] = 1        # write out cluster physical properties?
    subs['out_cluster_phot'] = 1   # write out cluster photometry?
    subs['out_cluster_spec'] = 1   # write out cluster specra?
    subs['out_cluster_yield'] = 0  # write out cluster yields?
    subs['output_mode'] = 'binary' # ascii or binary or fits
    
    for i,(logM_,n_trials_) in enumerate(zip(logM,n_trials)):
        fname = 'cluster_logM{0:02d}.param'.format(int(10.*logM_))
        
        subs['model_name'] = '{0:s}{1:02d}'.format(model_name_base,int(10.*logM_))
        subs['cluster_mass'] = 10.**logM_
        subs['n_trials'] = n_trials_

        # stringify values
        for k,v in subs.items():
            subs[k]=str(v)
            
        substitute_params(fname_def,fname,subs)
        
        ## print result
        if i == 0:
            w = 15 # width of field
            print '\n{0:{w}s} {1:>{w}s} {2:>{w}s}'.format(\
                'model_name'.center(w),'logM','n_trials',w=w)
    
        print '{0:{w}s} {1:>{w}.1f} {2:>{w}d}'.format(\
                subs['model_name'].center(w),logM_,n_trials_,w=w)

    # print ''
    # for k,v in subs.items():
    #     print k+":",v
        
if __name__ == '__main__':
    main()
