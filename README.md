
convfast
========

A tools to calculate multiple-input multiple-output (MIMO) FIR convolutions with less memory consumption using overlap-save method.


Requirments
-----------

* python3
* numpy



Usage
-----

Get repository

```
$ git clone https://github.com/penrin/convfast
$ cd convfast
```


Most basic command (4 arguments required):

```
$ python convfast.py -ni 80 -no 96 -i input.wav -f fir.wav
```

* -ni: number of channels of input signal
* -no: number of channels of output signal 
* -i: file name of input signals
* -f: file name of FIR filter




Help:

```
$ python convfast.py -h
usage: convfast.py [-h] -ni NI -no NO -i I -f F [-o O] [-fs FS] [-ws WS]
                   [-g GAIN] [-p FFTPOINT] [--split] [--limit] [--overwrite]

optional arguments:
  -h, --help            show this help message and exit
  -ni NI                number of input channel
  -no NO                number of output channel
  -i I                  input filename
  -f F                  FIR filename
  -o O                  output filename, default=out.wav
  -fs FS                sample rate (Hz), default=48000
  -ws WS                sample width (Byte), default=2
  -g GAIN, --gain GAIN  Gain (dB), default=0
  -p FFTPOINT, --fftpoint FFTPOINT
                        FFT point greater than FIR length
  --split               Divide the output into mono wav files
  --limit               limit the amplitude when overflow occurs
  --overwrite           Overwrite even if file already exists
```

File naming convention
----------------------



File format
-----------


### FIR


### Input


### Output



How about Overlap-save method
-----------------------------

![overlap-save](https://user-images.githubusercontent.com/8520833/50077302-5be19000-0227-11e9-8074-e4726ccd9722.png)
