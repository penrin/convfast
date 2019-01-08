import os, sys
import numpy as np
import convfast as cf
import audioproc as ap
import random
from scipy.signal import firwin
from subprocess import Popen


len_fir = 1025
len_input = 48000 * 60


path2work = 'benchmark_workfolder' 

if os.path.isdir(path2work):
    print('please remove directory \"%s\"' % path2work)
    sys.exit()
os.mkdir(path2work)




print('preparing...', end='')
sys.stdout.flush()


fir = firwin(len_fir, 0.25)
fir_1to1 = fir.reshape(1, 1, -1)
np.save('%s/fir_1to1.npy' % path2work, fir_1to1)

fir_10to10 = np.empty([10, 10, fir.shape[-1]])
fir_10to10[:, :, :] = fir_1to1 / 10
np.save('%s/fir_10to10.npy' % path2work, fir_10to10)

fir_100to100 = np.empty([100, 100, fir.shape[-1]])
fir_100to100[:, :, :] = fir_1to1 / 100
np.save('%s/fir_100to100.npy' % path2work, fir_100to100)

input_1 = np.random.randn(len_input).reshape(-1, 1)
input_1 /= ap.absmax(input_1)
ap.writewav('%s/input_1.wav' % path2work, input_1, ws=2)

input_10 = np.empty([input_1.shape[0], 10])
input_10[:, :] = input_1
ap.writewav('%s/input_10.wav' % path2work, input_10, ws=2)

input_100 = np.empty([input_1.shape[0], 100])
input_100[:, :] = input_1
ap.writewav('%s/input_100.wav' % path2work, input_100, ws=2)

del fir_1to1, fir_10to10, fir_100to100
del input_1, input_10, input_100

print('done')

print()
cmd = 'time python convfast.py -ni 1 -no 1 -i {path}/input_1.wav -f {path}/fir_1to1.npy -o {path}/out.wav --overwrite'.format(path=path2work)
proc = Popen(cmd, shell=True)
proc.wait()

print()
cmd = 'time python convfast.py -ni 10 -no 10 -i {path}/input_10.wav -f {path}/fir_10to10.npy -o {path}/out.wav --overwrite'.format(path=path2work)
proc = Popen(cmd, shell=True)
proc.wait()

print()
cmd = 'time python convfast.py -ni 100 -no 100 -i {path}/input_100.wav -f {path}/fir_100to100.npy -o {path}/out.wav --overwrite'.format(path=path2work)
proc = Popen(cmd, shell=True)
proc.wait()



cmd = 'rm -rf %s' % path2work
proc = Popen(cmd, shell=True)
proc.wait()

