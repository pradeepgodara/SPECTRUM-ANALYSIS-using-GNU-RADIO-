#!/usr/bin/env python
##################################################

# Generated: Thu Jul 30 13:35:08 2015
##################################################

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import fft
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from optparse import OptionParser
import osmosdr
import time
import os
import math
from threading import Timer
import httplib
import mimetypes
import urlparse

class top_block(gr.top_block):

    def __init__(self, cf):
        gr.top_block.__init__(self, "FM radio FFT example")

        ##################################################
        # Blocks
        ##################################################
        self.fft_vxx_0 = fft.fft_vcc(2048, True, (window.rectangular(2048)), True, 1)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, 2048)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_float*2048, "/home/pradeep/tutorial_btp/fm/out", False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(2048)
        self.RTL820T = osmosdr.source( args="numchan=" + str(1) + " " + "" )
        self.RTL820T.set_sample_rate(2.0E6)
        self.RTL820T.set_center_freq(cf, 0)
        self.RTL820T.set_freq_corr(00, 0)
        self.RTL820T.set_dc_offset_mode(0, 0)
        self.RTL820T.set_iq_balance_mode(0, 0)
        self.RTL820T.set_gain_mode(False, 0)
        self.RTL820T.set_gain(0, 0)
        self.RTL820T.set_if_gain(00000000000, 0)
        self.RTL820T.set_bb_gain(000000000000, 0)
        self.RTL820T.set_antenna("", 0)
        self.RTL820T.set_bandwidth(0, 0)
          

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.RTL820T, 0), (self.blocks_stream_to_vector_0, 0))
        #self.connect((self.fft_vxx_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_file_sink_0, 0))

def get_record_filename(cf):
    return "fft/%.2fHz" % cf

def record(cf, interval):
    tb = top_block(cf)
    timer = Timer(interval, after_record, args=[tb, cf])
    timer.start()
    tb.start()
    timer.join()

def after_record(tb, cf):
    tb.stop()
    tb.wait()

    import scipy
    vals = scipy.fromfile(open("out"), dtype=float)
    #print vals
    print len(vals)

    readings_per_sample = 2048
    samples = len(vals)/readings_per_sample
    sums = ([0] * readings_per_sample)
    for i in range(samples):
        sample = vals[i*readings_per_sample:(i+1)*readings_per_sample]
        for j in range(readings_per_sample):
            sums[j] += sample[j]
    for i in xrange(readings_per_sample):
        sums[i] /= samples 
         
    #print sums
    #for i in range(readings_per_sample):
     #print sums[i].imag ,sums[i].real 
     #print sums[i].real 
    print len(sums)
    x = [cf-1e6+i*(4e6/readings_per_sample) for i in range(readings_per_sample/2)]
    y = [10*(math.log10((sums[i])/10**5)) for i in range(readings_per_sample/2)]


      #if x[i] == cf:
        #y=0
    with open(get_record_filename(cf), "w") as f:
        f.write(str(zip(x, y)))

if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()

    scf = input("Starting central frequency (Example 92.7E6): ")
    ecf = input("Ending central frequency (Example 92.7E6): ")
    interval = input("Time interval (Example 5): ")
    
    ccf = scf
    while ccf <= ecf:
        print ">> Recording for Central Frequency = %f" % ccf
        print
        record(ccf, interval)
        ccf += 2e6
        print

    ccf = scf
    x, y = [], []
    #folder = os.path.abspath(os.path.dirname(__file__)) + "/plots/%s" % (time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))
    #os.mkdir(folder)
    while ccf <= ecf:
        with open(get_record_filename(ccf), "r") as f:
            vals = eval(f.read())
            vals = zip(*vals)
            x += list(vals[0])
            y += list(vals[1])
           # y =tuple(y[30]*len(y))

        ccf += 2e6
print len(y)
#y[:]=y[:]-30
#for i in range(len(y)):
 # y[i] -= 30
with open(get_record_filename(ccf), "w") as f:
        f.write(str(zip(x, y)))
#scipy.savetxt('scipy.txt', (x, y), header='x y', fmt='%g') 
for i in range(len(y)):
 y[i] -= 38  
 x[i]  /=1000000  
import matplotlib.pyplot as plt
print len(x)
plt.plot(x, y)
plt.xticks(range(int(x[0]), int(x[-1]+20), int(20)))
plt.yticks(range(int(-200),int(+40), int(20)))
plt.ylabel('Power (dB)')
plt.xlabel('Frequency (MHz)')
plt.grid(True)
#plt.ylim((-180,30))
plt.show()
print ccf

