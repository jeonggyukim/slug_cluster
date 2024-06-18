#!/usr/bin/env python

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

from slug_cluster import slug_cluster

def plot_Psi_Xi_hnu_evol(sc, ax, field='Lbol', band=None, percentile=(10, 90), stride=1, color='b'):
    
    """
    Plot evolution of conversion factors
    
    Parameters
    field: string
        'Lbol', 'L', 'Q'
    band: string
        required when field is 'L' or 'Q'.
        Available bands are 'H0' (hydrogen ionizing, >13.6eV), 'FUV' (6.0-13.6eV),
        and 'LW' (Lyman-Werner, 11.3-13.6eV)
    stride: integer
        show only subsamples
    """

    if field == 'Lbol':
        y = getattr(sc, 'Lbol')
        ymed = getattr(sc, 'Lbol_med')
    elif field in ['L', 'Q', 'hnu']:
        y = getattr(sc, field)[band]
        ymed = getattr(sc, field + '_med')[band]
        #if field == 'hnu': # to be fixed later
        #    ymed = ymed.value
    else:
        raise
    
    if field == 'hnu':
        y0 = 1.0
    else:
        y0 = sc.target_mass
        
    time=sc.time/1e6
    if stride > 0:
        for i in range(0, y.shape[0], stride):
            ax.plot(time, y[i,:]/y0, alpha=0.2)

    ax.fill_between(time,
                    np.percentile(y/y0, percentile[0], axis=0),
                    np.percentile(y/y0, percentile[1], axis=0), alpha=0.2, color=color)

    ax.plot(time, ymed/y0, '-', color=color, lw=3, zorder=3)
    
    ax.set_xlim(0, 1e1)
    
if __name__ == '__main__':

    cmap = mpl.cm.viridis
    norm = mpl.colors.Normalize(vmin=2.0, vmax=5.0)
    ##logM = [2.0, 2.6, 3.0, 4.0, 5.0]
    ##logM = [2.2, 2.4, 2.6, 2.8, 3.0]
    logM = [2.4, 2.6, 3.0, 4.0, 5.0]
    color = [cmap(norm(logM_)) for logM_ in logM]
    percentile = (10, 90)

    fig, axes = plt.subplots(3, 3, figsize=(18, 12), sharex=True)
    sc = slug_cluster()
    for logM_, color_ in zip(logM, color):
        out = sc.integrate_spec(logM=logM_, force_override=False, verbose=False)
        plot_Psi_Xi_hnu_evol(sc, axes[0, 0], field='L', band='H0', percentile=percentile, stride=0, color=color_)
        plot_Psi_Xi_hnu_evol(sc, axes[0, 1], field='L', band='FUV', percentile=percentile, stride=0, color=color_)
        plot_Psi_Xi_hnu_evol(sc, axes[0, 2], field='L', band='LW', percentile=percentile, stride=0, color=color_)
        plot_Psi_Xi_hnu_evol(sc, axes[1, 0], field='Q', band='H0', percentile=percentile, stride=0, color=color_)
        plot_Psi_Xi_hnu_evol(sc, axes[1, 1], field='Q', band='FUV', percentile=percentile, stride=0, color=color_)
        plot_Psi_Xi_hnu_evol(sc, axes[1, 2], field='Q', band='LW', percentile=percentile, stride=0, color=color_)
        plot_Psi_Xi_hnu_evol(sc, axes[2, 0], field='hnu', band='H0', percentile=percentile, stride=0, color=color_)
        plot_Psi_Xi_hnu_evol(sc, axes[2, 1], field='hnu', band='FUV', percentile=percentile, stride=0, color=color_)
        plot_Psi_Xi_hnu_evol(sc, axes[2, 2], field='hnu', band='LW', percentile=percentile, stride=0, color=color_)

    axes[0, 0].set_ylabel(r'$L(t)/M_{\rm cl,0}\;[L_{\odot}\,M_{\odot}^{-1}]$')
    axes[1, 0].set_ylabel(r'$Q(t)/M_{\rm cl,0}\;[{\rm phot}\,{\rm s}^{-1}\,M_{\odot}^{-1}]$')
    axes[2, 0].set_ylabel(r'$\langle h\nu \rangle$')

    for ax in axes[0, :]:
        ax.set_ylim(0, 1e3)

    for ax in axes[1, :]:
        ax.set_ylim(0, 1e47)

    for ax in axes[2, :]:
        ax.set_xlabel('age [Myr]')

    suptitle = [r'EUV ($>13.6\;{\rm eV})$', r'FUV ($6.0-13.6\;{\rm eV}$)', r'LW ($11.3-13.6\;{\rm eV}$)']
    for ax, suptitle_ in zip(axes[0, :], suptitle):
        ax.set_title(suptitle_, fontsize='larger')


    lines = [mpl.lines.Line2D([0, 1], [0, 1], color=c) for c in color]
    labels = [r'$\log_{10}\, M_{\rm cl, 0}$=' + '{0:4.1f}'.format(logM_) for logM_ in logM]

    axes[0, 0].legend(lines, labels, loc=1)
    axes[0, 2].annotate('(shades: 10th/90th percentile)', xy=(0.15, 0.9), xycoords='axes fraction')
    
    plt.tight_layout()
    
    #savname = os.path.join(os.path.expanduser('~'), 'Dropbox/Rad-slug-sim', 'Psi_Xi_hnu_evol.pdf')
    savname = './Psi_Xi_hnu_evol.pdf'
    plt.savefig(savname, dpi=200)

