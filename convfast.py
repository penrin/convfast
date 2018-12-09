import os, sys, glob
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
            i = self.indexlist_output[i]
            j = self.indexlist_input[i]
            fir[i, j, :] = one_fir.reshape(-1)    
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
        return np.load(self.
                filename)



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
            i = self.indexlist_output[i]
            j = self.indexlist_input[i]
            frames = w.readframes(nframes)
            if ws == 3:
                d = np.empty((nframes, 4), dtype=np.uint8)
                d[:, 1:] = np.frombuffer(frames, dtype=np.uint8).reshape(-1, 3)
                fir[i, j, :] = d.view(np.int32)[:, 0] / 2147483648
            elif ws == 2:
                fir[i, j, :] = np.frombuffer(frames, dtype=np.int16) / 32768
            elif ws == 4:
                fir[i, j, :] = np.frombuffer(frames, dtype=np.int32) / 2147483648
            w.close()
        return fir
