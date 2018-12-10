import os, sys
import glob
import shutil
import argparse
import time
import wave
import numpy as np



class Input():

    def __init__(self, filename, n_input):
        
        _, ext = os.path.splitext(filename)

        if ext == '.wav':
            if os.path.isfile(filename):
                self.input = _InputMultiWav(filename, n_input)
            else:
                self.input = _InputMonoWav(filename, n_input)

        elif ext == '.npy':
            if os.path.isfile(filename):
                self.input = _InputMultiNpy(filename, n_input)
            else:
                self.input = _InputMonoNpy(filename, n_input)
                
        else:
            message = '{} file is not supported.'.format(ext) 
            print(message)
            sys.exit()
        
        self.nframes = self.input.nframes
        return
        
    def close(self):
        self.input.close()
        return

    def readframes(self, n):
        return self.input.readframes(n)


class _InputMultiWav():

    def __init__(self, filename, n_input):
        self.wr = wave.open(filename, 'r')
        params = self.wr.getparams()
        self.nchannels = params[0]
        self.ws = params[1]
        self.fs = params[2]
        self.nframes = params[3]

        if self.nchannels != n_input:
            print('number of input channels does not match.')
            print('%s contains %d ch signals. != %d'\
                            % (filename, self.nchannels, n_input))
            sys.exit()

        self.pointer = 0
        return

    def close(self):
        self.wr.close()
        return

    def readframes(self, n):
        s = self.pointer
        e = s + n
        if e > self.nframes:
            e = self.nframes
        N = e - s
        frames = self.wr.readframes(N)
        if self.ws == 3:
            d = np.zeros((N * self.nchannels, 4), dtype=np.uint8)
            d[:, 1:] = np.frombuffer(frames, dtype=np.uint8).reshape(-1, 3)
            data = d.view(np.int32)[:, 0] / 2147483648
        elif self.ws == 2:
            data = np.frombuffer(frames, dtype=np.int16) / 32768
        elif self.ws == 4:
            data = np.frombuffer(frames, dtype=np.int32) / 2147483648
        data = data.reshape((self.nchannels, -1), order='F')
        
        self.pointer += e - s
        return data


class _InputMultiNpy():

    def __init__(self, filename, n_input):
        
        self.wr = np.load(filename, 'r')
        self.nchannels = self.wr.shape[0]

        if self.nchannels != n_input:
            print('number of input channels does not match.')
            print('%s contains %d ch signals. != %d'\
                            % (filename, self.nchannels, n_input))
            sys.exit()
        
        self.nframes = self.wr.shape[1]
        self.pointer = 0
        return

    def close(self):
        pass
        return

    def readframes(self, n):
        s = self.pointer
        e = s + n
        if e > self.nframes:
            e = self.nframes
        data = np.copy(self.wr[:, s:e])
        
        self.pointer += e - s
        return data
        
class _InputMonoWav():

    def __init__(self, filename, n_input):
        
        self.nchannels = n_input
        for ch in range(1, self.nchannels + 1):
            if not os.path.isfile(filename.format(i=ch)):
                print('input file does not exits.')
                print('->', filename.format(i=ch))
                sys.exit()
        
        self.wr = []
        for ch in range(1, self.nchannels + 1):
            w = wave.open(filename.format(i=ch))
            if w.getparams()[0] != 1:
                message = '%s is not monaural file.' % filename.format(i=ch)
                print(message)
                sys.exit()
            else:
                self.wr.append(w)
        
        params_ref = self.wr[0].getparams()
        self.ws = params_ref[1]
        self.fs = params_ref[2]
        self.nframes = params_ref[3]
        
        for i in range(1, self.nchannels):
            params = self.wr[i].getparams()
            if params[1] != self.ws:
                print('input sampwidth is not unified.')
                sys.exit()
            if params[2] != self.fs:
                print('input sample rate is not unified.')
                sys.exit()
            if params[3] != self.nframes:
                print('input length is not aligned.')
                sys.exit()
                
        self.pointer = 0
        return    

    def close(self):
        for i in range(self.nchannels):
            self.wr[i].close()
        return
    
    def readframes(self, n):
        s = self.pointer
        e = s + n
        if e > self.nframes:
            e = self.nframes
        N = e - s
        data = np.empty([self.nchannels, N])
        for i in range(self.nchannels):
            frames = self.wr[i].readframes(N)
            if self.ws == 3:
                d = np.zeros((N, 4), dtype=np.uint8)
                d[:, 1:] = np.frombuffer(frames, dtype=np.uint8).reshape(-1, 3)
                data[i, :] = d.view(np.int32)[:, 0] / 2147483648
            elif self.ws == 2:
                data[i, :] = np.frombuffer(frames, dtype=np.int16) / 32768
            elif self.ws == 4:
                data[i, :] = np.frombuffer(frames, dtype=np.int32) / 2147483648
        self.pointer += e - s
        return data


class _InputMonoNpy():

    def __init__(self, filename, n_input):
        
        self.nchannels = n_input
        for ch in range(1, self.nchannels + 1):
            if not os.path.isfile(filename.format(i=ch)):
                print('input file does not exits.')
                print('->', filename.format(i=ch))
                sys.exit()
        
        self.wr = []
        for ch in range(1, self.nchannels + 1):
            w = np.load(filename.format(i=ch), 'r')
            if w.size != max(w.shape):
                print('.npy contains multiple dimensions.', one_fir.shape)
                sys.exit()
            else:
                w_ = w.reshape(-1)
                self.wr.append(w_)
                
        self.nframes = self.wr[0].size
        for i in range(1, self.nchannels):
            if self.wr[i].size != self.nframes:
                print('input length is not aligned.')
                sys.exit()

        self.pointer = 0
        return
    
    def close(self):
        pass
    
    def readframes(self, n):
        s = self.pointer
        e = s + n
        if e > self.nframes:
            e = self.nframes
            
        data = np.empty([self.nchannels, e - s])
        for i in range(self.nchannels):
            data[i, :] = self.wr[i][s:e]
        
        self.pointer += e - s
        return data






class FIR():
    
    def __init__(self, filename, n_output, n_input):
        
        _, ext = os.path.splitext(filename)
        if ext == '.wav':
            if os.path.isfile(filename):
                print('signle \'%s\' file of FIR is not supported.' % ext)
                sys.exit()
            else:
                self.fir = _FIRMonoWav(filename, n_output, n_input)

        elif ext == '.npy':
            if os.path.isfile(filename):
                self.fir = _FIRMultiNpy(filename, n_output, n_input)
            else:
                self.fir = _FIRMonoNpy(filename, n_output, n_input)
        else:
            message = '{} file is not supported.'.format(ext) 
            print(message)
            sys.exit()
        
        self.len_fir = self.fir.len_fir
        return

    def read(self):
        return self.fir.read()


class _FIRMonoNpy():
    
    def __init__(self, filename, n_output, n_input):
        
        self.filename = filename
        self.n_output = n_output
        self.n_input = n_input

        self._get_FIR_list()
        self._get_len_fir()
        return

    def _get_len_fir(self):
        one_fir = np.load(self.filename_list[0], 'r')
        self.len_fir = one_fir.size
        return
    
    def _get_FIR_list(self):
        self.indexlist_input = []
        self.indexlist_output = []
        self.filename_list = []

        for i_input in range(self.n_input):
            ch_input = i_input + 1
            for i_output in range(self.n_output):
                ch_output = i_output + 1
                name_fmt = self.filename.format(i=ch_input, o=ch_output)
                if os.path.isfile(name_fmt):
                    self.indexlist_input.append(i_input)
                    self.indexlist_output.append(i_output)
                    self.filename_list.append(name_fmt)
        
        if len(self.filename_list) == 0:
            print('input file does not exits.')
            print('->', self.filename.format(i=ch_output, o=ch_output))
            sys.exit()
        return
    
    def read(self):
        fir = np.zeros([self.n_output, self.n_input, self.len_fir])
        for i in range(len(self.filename_list)):
            one_fir = np.load(self.filename_list[i], 'r')
            if one_fir.size != max(one_fir.shape):
                print('.npy contains multiple dimensions.', one_fir.shape)
                sys.exit()
            io = self.indexlist_output[i]
            ii = self.indexlist_input[i]
            fir[io, ii, :] = one_fir.reshape(-1)    
        return fir


class _FIRMultiNpy():

    def __init__(self, filename, n_output, n_input):
         
        fir = np.load(filename, 'r')
        if (fir.shape[0], fir.shape[1]) != (n_output, n_input):
            print('shape of %s is' % filename, fir_.shape)
            sys.exit()
        
        self.filename = filename
        self.n_output = n_output
        self.n_input = n_input
        self.len_fir = fir.shape[-1]
        return

    def read(self):
        return np.load(self.filename)


class _FIRMonoWav():

    def __init__(self, filename, n_output, n_input):
        
        self.filename = filename
        self.n_output = n_output
        self.n_input = n_input

        self._get_FIR_list()
        self._get_len_fir()
        return

    def _get_len_fir(self):
        w = wave.open(self.filename_list[-1], 'r')
        self.len_fir = w.getnframes()
        w.close()
        return
 
    def _get_FIR_list(self):
        self.indexlist_input = []
        self.indexlist_output = []
        self.filename_list = []

        for i_input in range(self.n_input):
            ch_input = i_input + 1
            for i_output in range(self.n_output):
                ch_output = i_output + 1
                name_fmt = self.filename.format(i=ch_input, o=ch_output)
                if os.path.isfile(name_fmt):
                    self.indexlist_input.append(i_input)
                    self.indexlist_output.append(i_output)
                    self.filename_list.append(name_fmt)

        if len(self.filename_list) == 0:
            print('input file does not exits.')
            print('->', self.filename.format(i=ch_output, o=ch_output))
            sys.exit()
        return
    
    def read(self):
        # read FIRs
        fir = np.zeros([self.n_output, self.n_input, self.len_fir])
        for i in range(len(self.filename_list)):
            w = wave.open(self.filename_list[i], 'r')
            params = w.getparams()
            nchannels = params[0]
            ws = params[1]
            nframes = params[3]
            
            if nchannels != 1:
                print('%s contains multiple channels' % self.filename_list[i])
                sys.exit()
            if nframes != self.len_fir:
                print('length of firs are not aligned')
                sys.exit()
                
            # read frames
            io = self.indexlist_output[i]
            ii = self.indexlist_input[i]
            frames = w.readframes(nframes)
            if ws == 3:
                d = np.empty((nframes, 4), dtype=np.uint8)
                d[:, 1:] = np.frombuffer(frames, dtype=np.uint8).reshape(-1, 3)
                fir[io, ii, :] = d.view(np.int32)[:, 0] / 2147483648
            elif ws == 2:
                fir[io, ii, :] = np.frombuffer(frames, dtype=np.int16) / 32768
            elif ws == 4:
                fir[io, ii, :] = np.frombuffer(frames, dtype=np.int32) / 2147483648
            w.close()
        return fir







class Output():

    def __init__(self, filename, n_output, ws, fs, split=False, overwrite=False):
        
        _, ext = os.path.splitext(filename)

        if ext == '.wav':
            if split == True:
                self.output = _OutputMonoWav(
                        filename, n_output, ws, fs, overwrite)
            else:
                self.output = _OutputMultiWav(
                        filename, n_output, ws, fs, overwrite)

        else:
            message = 'writing {} file is not supported.'.format(ext) 
            print(message)
            sys.exit()
    
    def check_already_exits(self):
        self.output.check_already_exits()

    def close(self):
        self.output.close()
        
    def writeframes(self, data, inplace=True):
        if inplace:
            return self.output.writeframes(data)
        else:
            return self.output.writeframes_noinplace(data)
    
    def tell_nframes(self):
        return self.output.nframes

class _OutputMultiWav():

    def __init__(self, filename, n_output, ws, fs, overwrite):
        
        if overwrite == False:        
            self.check_already_exits(filename)
        
        self.ww = wave.open(filename, 'wb')
        self.ww.setparams((n_output, ws, fs, 0, 'NONE', 'not compressed'))
        self.ws = ws
        self.n_output = n_output
        self.nframes = 0
    
    def close(self):
        self.ww.close()
        
    def check_already_exits(self, filename):
        
        if os.path.isfile(filename):
            msg = '\'%s\' already exists. Overwrite ? [y/n] ' % filename
            print(msg, end='')
            yesno = input()
            if yesno == 'n':
                sys.exit()
                
    
    def writeframes(self, data): # data is inplaced !!!!
        d = data.reshape(-1, order='F')
        if self.ws == 3:
            d *= 2147483647 # inplace !
            a32 = d.astype(np.int32)
            frames = a32.view(np.uint8).reshape(-1, 4)[:, 1:].tobytes()
        elif self.ws == 2:
            d *= 32767 # inplace !
            frames = d.astype(np.int16).tobytes()
        elif self.ws == 4:
            d *= 2147483647 # inplace !
            frames = d.astype(np.int32).tobytes()
        self.ww.writeframes(frames)
        self.nframes = self.ww.tell()
        return

    def writeframes_noinplace(self, data):
        if self.ws == 3:
            d = data.reshape(-1, order='F') * 2147483647
            a32 = d.astype(np.int32)
            frames = a32.view(np.uint8).reshape(-1, 4)[:, 1:].tobytes()
        elif self.ws == 2:
            d = data.reshape(-1, order='F') * 32767
            frames = d.astype(np.int16).tobytes()
        elif self.ws == 4:
            d = data.reshape(-1, order='F') * 2147483647
            frames = d.astype(np.int32).tobytes()
        self.ww.writeframes(frames)
        self.nframes = self.ww.tell()
        return


class _OutputMonoWav():
    
    def __init__(self, filename, n_output, ws, fs, overwrite):
        
        self.n_output = n_output
        self.ws = ws
        filename_list = self._make_filename_list(filename)

        if overwrite == False:        
            self.check_already_exits(filename)
            
        self.ww = []
        for i in range(n_output):
            w = wave.open(filename_list[i], 'wb')
            w.setparams((1, ws, fs, 0, 'NONE', 'not compressed'))
            self.ww.append(w)
        self.nframes = 0
            
    def check_already_exits(self, filename_list):
        
        exit = 0
        for filename in filename_list[::-1]:
            if os.path.isfile(filename):
                exit += 1
        
        if exit > 0:
            msg = '%d files such as \'%s\' already exist. Overwrite ? [y/n] '\
                    % (exit, filename)                
            print(msg, end='')
            yesno = input()
            if yesno == 'n':
                sys.exit()
        

    def close(self):
        for i in range(self.n_output):
            self.ww[i].close()

    def _make_filename_list(self, filename):
        filelist = []
        if filename.format(1) != filename.format(2):
            for ch in range(1, self.n_output + 1):
                filelist.append(filename.format(ch))
        elif filename.format(o=1) != filename.format(o=2):
            for ch in range(1, self.n_output + 1):
                filelist.append(filename.format(o=ch))
        else:
            root, ext = os.path.splitext(filename)
            digit = np.floor(np.log10(self.n_output)) + 1
            filename_ = root + '{:0%dd}' % digit + ext
            for ch in range(1, self.n_output + 1):
                filelist.append(filename_.format(ch))
        return filelist

    def writeframes(self, data):
        if self.ws == 3:
            data *= 2147483647 # inplace !
            for i in range(self.n_output):
                a32 = data[i, :].astype(np.int32)
                frames = a32.view(np.uint8).reshape(-1, 4)[:, 1:].tobytes()
                self.ww[i].writeframes(frames)
        elif self.ws == 2:
            data *= 32767 # inplace !
            for i in range(self.n_output):
                frames = data[i, :].astype(np.int16).tobytes()
                self.ww[i].writeframes(frames)
        elif self.ws == 4:
            data *= 2147483647 # inplace !
            for i in range(self.n_output):
                frames = data[i, :].astype(np.int32).tobytes()
                self.ww[i].writeframes(frames)
        self.nframes = self.ww[0].tell()
        return

    def writeframes_noinplace(self, data):
        if self.ws == 3:
            for i in range(self.n_output):
                a32 = (data[i, :] * 2147483647).astype(np.int32)
                frames = a32.view(np.uint8).reshape(-1, 4)[:, 1:].tobytes()
                self.ww[i].writeframes(frames)
        elif self.ws == 2:
            for i in range(self.n_output):
                frames = (data[i, :] * 32767).astype(np.int16).tobytes()
                self.ww[i].writeframes(frames)
        elif self.ws == 4:
            for i in range(self.n_output):
                frames = (data[i, :] * 2147483647).astype(np.int32).tobytes()
                self.ww[i].writeframes(frames)
        self.nframes = self.ww[0].tell()
        return



class ProgressBar():

    def __init__(self, bar_length=40, slug='#', space='-', tail='', countdown=True):

        self.bar_length = bar_length
        self.slug = slug
        self.space = space
        self.tail = tail
        self.countdown = countdown
        self.start_time = None
    
    
    def bar(self, percent, end=1):
        percent = percent / end

        if self.countdown == True:
            if self.start_time == None:
                self.start_time = time.perf_counter()
                self.start_parcent = percent
                remain = 'Remain --:--:--'
            else:
                elapsed_time = time.perf_counter() - self.start_time
                progress = percent - self.start_parcent
                remain_t =  (elapsed_time / progress) * (1 - percent)
                h = remain_t // 3600
                m = remain_t % 3600 // 60
                s = np.ceil(remain_t % 60)
                remain = 'Remain %02d:%02d:%02d' % (h, m, s) 
        else:
            remain = ''
        
        len_slugs = int(percent * self.bar_length)
        slugs = self.slug * len_slugs
        spaces = self.space * (self.bar_length - len_slugs)
        txt = '\r[{bar}] {percent:.1%} {remain} {tail}'.format(
                bar=(slugs + spaces), percent=percent,
                remain=remain, tail=self.tail)
        if percent == 1:
            txt += '\n'
            self.start_time = None
        sys.stdout.write(txt)
        sys.stdout.flush()
        


def nextpow2(n):
    l = np.ceil(np.log2(n))
    m = int(np.log2(2 ** l))
    return m



if __name__ == '__main__':
    
    startRealTime = time.perf_counter()
    startClockTime = time.process_time()

    parser = argparse.ArgumentParser()
    parser.add_argument('-ni', type=int, help='number of input channel', required=True)
    parser.add_argument('-no', type=int, help='number of output channel', required=True)
    parser.add_argument('-i', type=str, help='input filename', required=True)
    parser.add_argument('-f', type=str, help='FIR filename', required=True)
    parser.add_argument('-o', type=str, default='out.wav', help='output filename, default=out.wav')
    parser.add_argument('-fs', type=int, default=48000, help='sample rate (Hz), default=48000')
    parser.add_argument('-ws', type=int, default=3, help='sample width (Byte), default=2')
    parser.add_argument('-g', '--gain', type=int, default=0, help='Gain (dB), default=0')
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
    
    

    # Setting parameter of overlap-save method
    ff = FIR(filename_fir, n_output, n_input)
    ii = Input(filename_in, n_input)

    # FIR length
    len_fir = ff.len_fir
    M = len_fir
    
    # FFT point
    if fftpoint < len_fir:
        N = 2 ** nextpow2(2 * M - 1)
    else:
        N = fftpoint
    
    # Block length & number
    L = N - M + 1
    len_input = ii.nframes
    nblocks = int(np.ceil((len_input + M - 1) / L))
    
    len_output = len_input + len_fir - 1

    text = 'convfast (https://github.com/penrin/convfast)\n'
    text += 'Stream:\n'
    text += '  Input %d ch, %d taps -> FIR %d taps -> Output %d ch, %d taps\n'\
            % (n_input, len_input, len_fir, n_output, len_output)
    text += '  Optional gain %d dB\n' % args.gain
    text += 'Overlap-save parameters:\n'
    text += '  Overlap (M-1)    %7d\n' % (M - 1)
    text += '  FFT point (N)    %7d\n' % N
    text += '  Block length (L) %7d\n' % L
    text += '  nBlocks          %7d\n' % nblocks
    text += '-' * shutil.get_terminal_size().columns + '\n'
    sys.stdout.write(text); #sys.stdout.flush()
    
    

    # Import FIR
    sys.stdout.write('Importing FIR...'); sys.stdout.flush()
    fir = ff.read()
    
    fir_sum = np.sum(np.abs(fir), axis=-1)
    n_zero_fir = np.sum(fir_sum == 0)
    sys.stdout.write('done')    
    if n_zero_fir > 0:
        text = ' -> %d items' % (fir_sum.size)        
        text += ' (%d items are zero signal)\n' % (n_zero_fir)
        sys.stdout.write(text)
    else:
        text = ' -> %d items\n' % (fir_sum.size)        
        sys.stdout.write(text)
    sys.stdout.flush()


    sys.stdout.write('FFT FIR...'); sys.stdout.flush()
    fir_f = np.fft.rfft(fir, n=N)
    del fir
    sys.stdout.write('done\n'); sys.stdout.flush()
    

    # convoluve
    print('Calculating convolution')
    oo = Output(filename_out, n_output, ws, fs, flg_split, flg_overwrite)
    
    block = np.empty([n_input, 1, N])
    block[:, 0, L:] = 0.

    remain_read = len_input
    remain_write = len_output
    
    pg = ProgressBar(countdown=True)
    for l in range(nblocks):
        pg.bar(l, nblocks)
        
        # overlap M-1 (=L)
        block[:, 0, :-L] = block[:, 0, L:]

        # Read input block
        if remain_read >= L:
            block[:, 0, -L:] = ii.readframes(L)
            remain_read -= L
        else:
            block[:, 0, -L:-L+remain_read] = ii.readframes(remain_read)
            block[:, 0, -L+remain_read:] = 0
            remain_read = 0
        

        # convolution
        block_f = np.fft.rfft(block, n=fftpoint)

        # np.matmul is actually faster when "row-major" dnarray are entered
        out_f = np.matmul(
                fir_f.transpose(2, 0, 1), block_f.transpose(2, 0, 1)
                ).transpose(1, 2, 0)
        
        out = np.fft.irfft(out_f) * gain


        # write
        if remain_write >= L:
            oo.writeframes(out[:, 0, -L:])
            remain_write -= L
        else:
            oo.writeframes(out[:, 0, -L:-L+remain_write])
            remain_write = 0

    pg.bar(1)
    
    

    # The end
    text = '%d taps were written\n' % oo.tell_nframes()
    ii.close()
    oo.close()
    
    text += '-' * shutil.get_terminal_size().columns + '\n'
    text += ' Real Time: %.2f sec\n' % (time.perf_counter() - startRealTime)
    text += 'Clock Time: %.2f sec' % (time.process_time() - startClockTime)
    print (text)
    
