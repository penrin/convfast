
convfast
========

A tools to calculate multiple-input multiple-output (MIMO) FIR convolutions.
The calculation uses the overlap-save method, which can be calculated efficiently with less memory consumption even when the input signal length is relatively long.

*Diagram of overlap-save method (single-input single-output):*
![overlap-save](https://user-images.githubusercontent.com/8520833/50077302-5be19000-0227-11e9-8074-e4726ccd9722.png "test")

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




File format & naming
------------------------

### FIR

* **Single `.npy` file of 3D array**
–
This ndarray must have this order: (Number of outputs, Number of inputs, Number of taps). The number of inputs and outputs of the array must match those specified in the option `-ni` and `-no`.
Filename must have the extension `.npy`.

* **Multiple `.npy` files of 1D array**
–
Multiple `.npy` files with MIMO FIR waveform data stored for each track.
Each data is usually a one-dimensional array. 
Multidimensional arrays are reshaped into one-dimensional arrays and read.
Filename must have the extension `.npy`, and include the input and output channel numbers that are counted up from 1 in the filename.

* **Multiple `.wav` files of mono**
–
Multiple `.wav` files with MIMO FIR waveform data stored for each track.
Each file must be a mono track. 
Filename must have the extension `.wav`, and include the input and output channel numbers that are counted up from 1 in the filename.


To specify multiple `.npy`/`.wav` files as options,
input and output numbers are represented by `{i}` and `{o}`, respectively.
Since this function uses the `format()` method, the format specifiers described in PEP3101 can be used.
For example, if you specify the following options,

```
-ni 2 -no 3 -f fir_out{o:02d}_in{i}.wav
```
it will try to read the following six files:

```
fir_out01_in1.wav  fir_out01_in2.wav  fir_out02_in1.wav
fir_out02_in2.wav  fir_out03_in1.wav  fir_out03_in2.wav
```
At this time, if some files do not exist, they are treated as zero signal.




### Input

* **Single `.wav` file of multi-track**
–
The number of tracks must be match those specified in the option `-ni`.
Filename must have the extension `.wav`.

* **Single `.npy` file of 2D array**
–
The array must have this order: (Number of tracks, Number of taps).
The number of tracks must be match those specified in the option `-ni`.
Filename must have the extension `.npy`.

* **Multiple `.wav` files of mono**
–
Multiple `.wav` files with input waveform data stored for each track.
Each file must be a mono track. 
Filename must have the extension `.wav`, and include the input channel numbers that are counted up from 1 in the filename.

* **Multiple `.npy` files of 1D array**
–
Multiple `.npy` files with input waveform data stored for each track.
Each data is usually a one-dimensional array. 
Multidimensional arrays are reshaped into one-dimensional arrays and read.
Filename must have the extension `.npy`, and include the input channel numbers that are counted up from 1 in the filename.


To specify multiple .npy/.wav files as options, input number is represented by {i}. For example, if you specify the following options,

```
-ni 80 -i input_{i:02d}.wav
```

it will try to read the following 80 files:

```
input_01.wav  input_02.wav  ...  input_80.wav
```




### Output

* **Single `.wav` files of multi-track**
–
Without the option `--split`, the output is written to a multi-track `.wav` file.
The filename is specified by `-o`.


* **Multiple `.wav` files of mono**
–
With the option `--split`, the output is written to multiple single-track `.wav` files.
The filename is specified by `-o`, where track number is represented by {o}. If you do not add {o}, a number is automatically added to the end of the filename.



