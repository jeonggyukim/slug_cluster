
#!/usr/bin/env python

import numpy as np

from slugpy import read_cluster_spec,read_cluster_phot,read_cluster_prop
from slug_cluster import slug_cluster

sc = slug_cluster()
time = 1.5e5
logM = sc.logM_all
LFUV0 = []
QH0 = []
hnuFUV0 = []
hnuH0 = []
Lbol0 = []
indx = 0     # indx = 0 <-> time = 10**5 yr

for logM_ in logM:
    sc.integrate_spec(logM_, verbose=False)
    LFUV0.append(sc.L['FUV'][:, indx])
    QH0.append(sc.Q['H0'][:, indx])
    Lbol0.append(sc.Lbol[:, indx])
    hnuFUV0.append(sc.hnu['FUV'][:, indx])
    hnuH0.append(sc.hnu['H0'][:, indx])

Lbol0 = np.array(Lbol0)
LFUV0 = np.array(LFUV0)
QH0 = np.array(QH0)
hnuFUV0 = np.array(hnuFUV0)
hnuH0 = np.array(hnuH0)

def write_to_txt(name='LFUV0'):
    with open(name + '.txt', 'wb') as f:
        # write header
        for logM_ in logM[:-1]:
            f.write('{0:>11s} '.format('logM' + '{0:02d}'.format(int(10.0*logM_))))
        f.write('{0:>11s}'.format('logM' + '{0:02d}'.format(int(10.0*logM[-1]))))
        f.write('\n')
        # save numpy array
        np.savetxt(f, np.transpose(globals()[name]), fmt='%.5e', delimiter=' ')

write_to_txt('LFUV0')
write_to_txt('QH0')
write_to_txt('Lbol0')
write_to_txt('hnuH0')
write_to_txt('hnuFUV0')
