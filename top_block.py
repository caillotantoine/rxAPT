#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: rx APT
# Author: Antoine CAILLOT
# Description: Receive and decode APT images from NOAA satellites
# GNU Radio version: 3.7.13.5
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

from PyQt4 import Qt
from PyQt4.QtCore import QObject, pyqtSlot
from datetime import datetime
from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import qtgui
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.qtgui import Range, RangeWidget
from optparse import OptionParser
import os.path
import sip
import sys
import time
from gnuradio import qtgui


class top_block(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "rx APT")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("rx APT")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "top_block")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())


        ##################################################
        # Variables
        ##################################################
        self.path_to_save_dir = path_to_save_dir = os.path.expanduser("~/Desktop")
        self.samp_rate = samp_rate = 2205000
        self.rf_gain = rf_gain = 20
        self.if_gain = if_gain = 40
        self.freq = freq = 137.62e6
        self.file_path = file_path = path_to_save_dir + "/APT_" + datetime.now().strftime("%d%m%Y_%H%M")

        ##################################################
        # Blocks
        ##################################################
        self._rf_gain_range = Range(0, 45, 5, 20, 200)
        self._rf_gain_win = RangeWidget(self._rf_gain_range, self.set_rf_gain, 'RF Gain', "counter_slider", float)
        self.top_grid_layout.addWidget(self._rf_gain_win)
        self._if_gain_range = Range(1, 80, 5, 40, 200)
        self._if_gain_win = RangeWidget(self._if_gain_range, self.set_if_gain, 'IF Gain', "counter_slider", float)
        self.top_grid_layout.addWidget(self._if_gain_win)
        self._freq_options = (137.62e6, 137.9125e6, 137.1e6, 99.8e6, )
        self._freq_labels = ('NOAA-15 (137.62MHz)', 'NOAA-18 (137.9125MHz)', 'NOAA-19 (137.1MHz)', 'Test FM', )
        self._freq_tool_bar = Qt.QToolBar(self)
        self._freq_tool_bar.addWidget(Qt.QLabel('Frequency'+": "))
        self._freq_combo_box = Qt.QComboBox()
        self._freq_tool_bar.addWidget(self._freq_combo_box)
        for label in self._freq_labels: self._freq_combo_box.addItem(label)
        self._freq_callback = lambda i: Qt.QMetaObject.invokeMethod(self._freq_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._freq_options.index(i)))
        self._freq_callback(self.freq)
        self._freq_combo_box.currentIndexChanged.connect(
        	lambda i: self.set_freq(self._freq_options[i]))
        self.top_grid_layout.addWidget(self._freq_tool_bar)
        self.uhd_usrp_source_0 = uhd.usrp_source(
        	",".join(("", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_center_freq(freq, 0)
        self.uhd_usrp_source_0.set_gain(rf_gain, 0)
        self.uhd_usrp_source_0.set_antenna('TX/RX', 0)
        self.uhd_usrp_source_0.set_bandwidth(samp_rate, 0)
        self.uhd_usrp_source_0.set_auto_dc_offset(True, 0)
        self.uhd_usrp_source_0.set_auto_iq_balance(True, 0)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=1,
                decimation=samp_rate/44100,
                taps=None,
                fractional_bw=None,
        )
        self.qtgui_sink_x_0 = qtgui.sink_c(
        	1024, #fftsize
        	firdes.WIN_BLACKMAN_hARRIS, #wintype
        	freq, #fc
        	samp_rate, #bw
        	"", #name
        	True, #plotfreq
        	True, #plotwaterfall
        	True, #plottime
        	True, #plotconst
        )
        self.qtgui_sink_x_0.set_update_time(1.0/10)
        self._qtgui_sink_x_0_win = sip.wrapinstance(self.qtgui_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_sink_x_0_win)

        self.qtgui_sink_x_0.enable_rf_freq(False)



        self.low_pass_filter_1 = filter.fir_filter_ccf(1, firdes.low_pass(
        	1, samp_rate, 40000, 4100, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_0 = filter.fir_filter_fff(1, firdes.low_pass(
        	5, 11025, 2400, 100, firdes.WIN_HAMMING, 6.76))
        self.fractional_interpolator_xx_0_0 = filter.fractional_interpolator_ff(0, 4.8/4.16)
        self.fractional_interpolator_xx_0 = filter.fractional_interpolator_ff(0, 1.1484375)
        self.blocks_wavfile_sink_1 = blocks.wavfile_sink(file_path+"_rawIQ.wav", 2, samp_rate, 8)
        self.blocks_wavfile_sink_0_0 = blocks.wavfile_sink(file_path+".wav", 1, 4160, 8)
        self.blocks_wavfile_sink_0 = blocks.wavfile_sink(file_path+".wav", 1, 11025, 8)
        self.blocks_multiply_xx_0 = blocks.multiply_vff(1)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vcc((if_gain, ))
        self.blocks_float_to_uchar_0 = blocks.float_to_uchar()
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_char*1, file_path+".dat", False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.blocks_deinterleave_0 = blocks.deinterleave(gr.sizeof_float*1, 1)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)
        self.blocks_complex_to_float_0 = blocks.complex_to_float(1)
        self.audio_sink_0 = audio.sink(44100, '', False)
        self.analog_rail_ff_0 = analog.rail_ff(0, 1)
        self.analog_fm_demod_cf_0_0 = analog.fm_demod_cf(
        	channel_rate=44100,
        	audio_decim=1,
        	deviation=75000,
        	audio_pass=18000,
        	audio_stop=20000,
        	gain=1.0,
        	tau=75e-6,
        )
        self.analog_fm_demod_cf_0 = analog.fm_demod_cf(
        	channel_rate=44100,
        	audio_decim=4,
        	deviation=75000,
        	audio_pass=15000,
        	audio_stop=16000,
        	gain=1.0,
        	tau=75e-6,
        )
        self.analog_const_source_x_0 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 255)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_const_source_x_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.analog_fm_demod_cf_0, 0), (self.blocks_wavfile_sink_0, 0))
        self.connect((self.analog_fm_demod_cf_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.analog_fm_demod_cf_0_0, 0), (self.audio_sink_0, 0))
        self.connect((self.analog_rail_ff_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.blocks_complex_to_float_0, 1), (self.blocks_wavfile_sink_1, 1))
        self.connect((self.blocks_complex_to_float_0, 0), (self.blocks_wavfile_sink_1, 0))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.fractional_interpolator_xx_0_0, 0))
        self.connect((self.blocks_deinterleave_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.blocks_deinterleave_0, 1), (self.blocks_float_to_complex_0, 1))
        self.connect((self.blocks_float_to_complex_0, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.blocks_float_to_uchar_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.low_pass_filter_1, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.qtgui_sink_x_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_float_to_uchar_0, 0))
        self.connect((self.fractional_interpolator_xx_0, 0), (self.blocks_deinterleave_0, 0))
        self.connect((self.fractional_interpolator_xx_0_0, 0), (self.analog_rail_ff_0, 0))
        self.connect((self.fractional_interpolator_xx_0_0, 0), (self.blocks_wavfile_sink_0_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.fractional_interpolator_xx_0, 0))
        self.connect((self.low_pass_filter_1, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.analog_fm_demod_cf_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.analog_fm_demod_cf_0_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_complex_to_float_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.blocks_multiply_const_vxx_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "top_block")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_path_to_save_dir(self):
        return self.path_to_save_dir

    def set_path_to_save_dir(self, path_to_save_dir):
        self.path_to_save_dir = path_to_save_dir
        self.set_file_path(self.path_to_save_dir + "/APT_" + datetime.now().strftime("%d%m%Y_%H%M"))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)
        self.uhd_usrp_source_0.set_bandwidth(self.samp_rate, 0)
        self.qtgui_sink_x_0.set_frequency_range(self.freq, self.samp_rate)
        self.low_pass_filter_1.set_taps(firdes.low_pass(1, self.samp_rate, 40000, 4100, firdes.WIN_HAMMING, 6.76))

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain
        self.uhd_usrp_source_0.set_gain(self.rf_gain, 0)


    def get_if_gain(self):
        return self.if_gain

    def set_if_gain(self, if_gain):
        self.if_gain = if_gain
        self.blocks_multiply_const_vxx_0.set_k((self.if_gain, ))

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self._freq_callback(self.freq)
        self.uhd_usrp_source_0.set_center_freq(self.freq, 0)
        self.qtgui_sink_x_0.set_frequency_range(self.freq, self.samp_rate)

    def get_file_path(self):
        return self.file_path

    def set_file_path(self, file_path):
        self.file_path = file_path
        self.blocks_wavfile_sink_1.open(self.file_path+"_rawIQ.wav")
        self.blocks_wavfile_sink_0_0.open(self.file_path+".wav")
        self.blocks_wavfile_sink_0.open(self.file_path+".wav")
        self.blocks_file_sink_0.open(self.file_path+".dat")


def main(top_block_cls=top_block, options=None):

    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
