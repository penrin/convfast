from convfast import *
import argparse
import time
import shutil



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-ni', type=int, help='number of input channel', required=True)
    parser.add_argument('-no', type=int, help='number of output channel', required=True)
    parser.add_argument('-i', type=str, help='input filename', required=True)
    parser.add_argument('-f', type=str, help='FIR filename', required=True)
    parser.add_argument('-o', type=str, default='out.wav', help='output filename, default=out.wav')
    parser.add_argument('-fs', type=int, default=48000, help='sample rate (Hz), default=48000')
    parser.add_argument('-ws', type=int, default=3, help='sample width (Byte), default=2')
    parser.add_argument('-g', '--gain', type=float, default=0, help='Gain (dB), default=0')
    parser.add_argument('-p', '--fftpoint', type=int, default=0, help='FFT point greater than FIR length')
    parser.add_argument('--split', action='store_true', help='Divide the output into mono wav files')
    parser.add_argument('--limit', action='store_true', help='limit the amplitude when overflow occurs')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite even if file already exists')


    args = parser.parse_args()
    filename_in = args.i
    filename_fir = args.f
    filename_out = args.o
    n_input = args.ni
    n_output = args.no
    flg_split = args.split
    flg_limit = args.limit
    flg_overwrite = args.overwrite
    ws = args.ws
    fs = args.fs
    gain = 10 ** (args.gain / 20)
    fftpoint = args.fftpoint
    
    
    startRealTime = time.perf_counter()
    startClockTime = time.process_time()
    
    main(n_input, n_output, filename_fir, filename_in, filename_out, 
            fftpoint, ws, fs, gain, flg_split, flg_limit, flg_overwrite)

    text += ' Real Time: %.2f sec\n' % (time.perf_counter() - startRealTime)
    text += 'Clock Time: %.2f sec\n' % (time.process_time() - startClockTime)
    text += '-' * shutil.get_terminal_size().columns
    print (text)



