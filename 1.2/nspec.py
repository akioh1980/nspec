#!/usr/bin/env python
#DSO-X4024A
from PyQt5 import QtCore, QtGui, QtWidgets
### additional modules ###
import subprocess
import time
from datetime import datetime
from matplotlib import pyplot as plt
import sys
import os
import numpy as np
import pandas as pd
#import random
import glob 
import scipy.fftpack as sf
import scipy as sp
import threading
import socket
from contextlib import closing
#from concurrent.futures import ThreadPoolExecutor, Future, as_completed


# user interface
from DSOX4024A_ui import Ui_MainWindow
import visa
# Import files
import sxs_fft_lite as sxs
version = "1.2"
progname = os.path.basename("%s (ver. %s)" % (sys.argv[0], version))

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)


class AppWindow_DSOX4024A(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.MainWindow = Ui_MainWindow()
        self.MainWindow.setupUi(self)
        self.statusBar().showMessage("DSO-X4024A/NspecAnalyzer", 2000)
        self.MainWindow.pushButton_quit.clicked.connect(self.fileQuit)
        self.MainWindow.pushButton_connect.clicked.connect(self.connect_DSOX4024A)
        #self.MainWindow.pushButton_connect.clicked.connect(self.connect_DSOX4024A_TCP)
        self.MainWindow.pushButton_select.clicked.connect(self.showDialog)
        self.MainWindow.pushButton_send_command.clicked.connect(self.send_command)
        self.MainWindow.pushButton_send_setup.clicked.connect(self.send_setup)
        self.MainWindow.pushButton_save.clicked.connect(self.save_command)         
        self.tdatetime = datetime.now()        
        tstr = self.tdatetime.strftime('%Y-%m-%d %H:%M:%S')
        self.MainWindow.label_Time_Begin.setText(_translate("Form",tstr, None))
        self.MainWindow.label_Time_Current.setText("./data/%s" % str(self.tdatetime.strftime("%y%m%d%H%M%S")))     
        #############################
        #nspec
        #############################
        self.MainWindow.pushButton_abort.clicked.connect(self.nspec_abort)
        self.MainWindow.pushButton_start.clicked.connect(self.nspec_start)
        self.MainWindow.checkBox_2k.stateChanged.connect(self.state_2k)
        self.MainWindow.checkBox_20k.stateChanged.connect(self.state_20k)
        self.MainWindow.checkBox_200k.stateChanged.connect(self.state_200k)
        self.MainWindow.checkBox_manual.stateChanged.connect(self.state_manual)
        self.MainWindow.pushButton_plot.clicked.connect(self.plot_psd_avg)
        self.dt_200kHz = ''
        self.dt_20kHz = ''
        self.dt_2kHz = ''            
        self.filename = ""
        self.state_2k_value = 0
        self.state_20k_value = 0
        self.state_200k_value = 0
        self.state_manual_value = 0
        self.s = 0
        self.count = 0        
        self.timer = QtCore.QTimer()
        self.state_start = 0
        #############################
        self.config_value_ain = ['V','T','T2','P','DEV','AIR']
        self.handle = ""
        self.client = ""
        self.labjackT7_usb = 0
        self.labjackT7_tcp = 0
        self.data = []
        self.labjackT7_tc0_panel = 0
        self.ain = [0,0,0,0,0,0]
        self.ain_v = [0,0,0,0,0,0]        
        self.dt_app = []
        self.yvalue_app_ain = [[],[],[],[],[],[]]
        self.plot_DSOX4024A_ch = [[],[],[],[],[],[]]
        callist1 = [
            'linear',
            'log',
        ]
        self.ain0 = ""

    def showDialog(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', './comm/')
        # fname[0] means path to the selected file.
        self.MainWindow.lineEdit_Setup.setText(fname[0])
        if fname[0]:
            # read file
            with open(fname[0], 'r') as f:
                data = f.read()
                self.MainWindow.textEdit_command.setText(data)

    def send_command(self):
        line = self.MainWindow.lineEdit_command.text()
        print "start at %s." % str(self.tdatetime)
        print line        
        if  line[-1] == '?':
            query = self.inst_dsox4024a.query(line)
            print query
        else:
            self.inst_dsox4024a.write(line)

        time.sleep(1.0)
        print "end at %s." % str(self.tdatetime)

    def read_preamble(self):
        line = ':WAVEFORM:PREAMBLE?'
        print "read preamble at %s." % str(self.tdatetime)        
        #print "start at %s." % str(self.tdatetime)
        preamble = self.inst_dsox4024a.query(line)
        if preamble.split(',')[0] == '+0':
            frmt = 'BYTE'
        elif preamble.split(',')[0] == '+1':
            frmt = 'WORD'
        elif preamble.split(',')[0] == '+4':
            frmt = 'ASCII'
        if preamble.split(',')[1] == '+0':
            typ = 'NORMAL'
        elif preamble.split(',')[1] == '+1':
            typ = 'PEAK DETECT'
        elif preamble.split(',')[1] == '+2':
            typ = 'AVERAGE'
        time.sleep(1.0)            
        #print "end at %s." % str(self.tdatetime)
        self.MainWindow.lineEdit_preamble_format.setText(str(frmt))
        self.MainWindow.lineEdit_preamble_type.setText(str(typ))
        self.MainWindow.lineEdit_preamble_point.setText(preamble.split(',')[2])
        self.MainWindow.lineEdit_preamble_count.setText(preamble.split(',')[3])
        self.MainWindow.lineEdit_preamble_xincrement.setText(preamble.split(',')[4])
        self.MainWindow.lineEdit_preamble_xorigin.setText(preamble.split(',')[5])
        self.MainWindow.lineEdit_preamble_xreference.setText(preamble.split(',')[6])
        self.MainWindow.lineEdit_preamble_yincrement.setText(preamble.split(',')[7])
        self.MainWindow.lineEdit_preamble_yorigin.setText(preamble.split(',')[8])
        self.MainWindow.lineEdit_preamble_yreference.setText(preamble.split(',')[9])        
        
    def send_setup(self):
        fname = self.MainWindow.lineEdit_Setup.text()
        print "start at %s." % str(self.tdatetime)
        with open(fname, 'r') as f:
            line = f.readline()
            while line:
                line = f.readline()
                test = '#' in line 
                if test == True:
                    print line
                else:
                    self.inst_dsox4024a.write(line)
                    print line
                    time.sleep(1.0)
        print "end at %s." % str(self.tdatetime)

    def send_setup_tcp(self):
        fname = self.MainWindow.lineEdit_Setup.text()
        host = self.MainWindow.lineEdit_IP.text()
        port = self.MainWindow.lineEdit_PORT.text()
        bufsize = self.MainWindow.lineEdit_BUFSIZE.text()
        print "start at %s." % str(self.tdatetime)
        with open(fname, 'r') as f:
            line = f.readline()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                        
            while line:
                line = f.readline()
                test = '#' in line 
                if test == True:
                    print line
                else:
                    sock.connect((host,port))
                    sock.send(line)
                    #self.inst_dsox4024a.write(line)
                    print line
                    time.sleep(1.0)
        print "end at %s." % str(self.tdatetime)
        
    def send_command_nspec(self, fname):
        print "start at %s." % str(self.tdatetime)
        with open(fname, 'r') as f:
            line = f.readline()
            while line:
                line = f.readline()
                test = '#' in line 
                if test == True:
                    print line
                else:
                    self.inst_dsox4024a.write(line)
                    print line
                    time.sleep(1.0)
        print "end at %s." % str(self.tdatetime)

    def send_command_nspec_tcp(self, fname):
        host = self.MainWindow.lineEdit_IP.text()
        port = self.MainWindow.lineEdit_PORT.text()
        bufsize = self.MainWindow.lineEdit_BUFSIZE.text()
        print "start at %s." % str(self.tdatetime)
        with open(fname, 'r') as f:
            line = f.readline()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)            
            while line:
                line = f.readline()
                test = '#' in line 
                if test == True:
                    print line
                else:
                    #self.inst_dsox4024a.write(line)
                    sock.connect((host,port))
                    sock.send(line)
                    print line
                    time.sleep(1.0)
        print "end at %s." % str(self.tdatetime)
        
    def save_command(self):
        f = self.MainWindow.textEdit_command.toPlainText()
        fname = self.MainWindow.lineEdit_Setup.text()
        with open(fname,'w') as file:
            file.write(f)
            print 'write and save to the selected file".'
            
    def connect_DSOX4024A(self):
        #try:
        #self.rm = visa.ResourceManager()
            self.rm = visa.ResourceManager('@py')
            print self.MainWindow.lineEdit_IP.text()
            self.inst_dsox4024a = self.rm.open_resource(u'TCPIP0::%s::INSTR' % (str(self.MainWindow.lineEdit_IP.text())) )
            idn = self.inst_dsox4024a.query(u'*IDN?')
            print idn
            self.MainWindow.lineEdit_Manufacturer.setText(idn.split(',')[0])
            self.MainWindow.lineEdit_Model.setText(idn.split(',')[1])
            self.MainWindow.lineEdit_SN.setText(idn.split(',')[2])
            self.MainWindow.lineEdit_SoftVersion.setText(idn.split(',')[3])  
            self.statusBar().showMessage("Nspec Analyzer for DSO-X4024A",2000)
            self.inst_dsox4024a.write('*RST')
            self.connection_dsox4024a = 1
        #except (IOError, AttributeError, TypeError, visa.VisaIOError) as e:
        #    self.connection_dsox4024a = 0
        #    pass

    def connect_DSOX4024A_TCP(self):
        try:
            host = self.MainWindow.lineEdit_IP.text()
            host0 = int(host.split('.')[0])
            host1 = int(host.split('.')[1])
            host2 = int(host.split('.')[2])
            host3 = int(host.split('.')[3])
            port = self.MainWindow.lineEdit_PORT.text()
            bufsize = int(self.MainWindow.lineEdit_BUFSIZE.text())
            print host, port, bufsize
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            with closing(sock):
                sock.connect( ('%d.%d.%d.%d' % (host0,host1,host2,host3) , int(port)) )
                sock.send(b'*IDN?')
                while True:
                    print(sock.recv(bufsize))
                #idn = str(sock.recv(bufsize))
                #print idn
                #self.MainWindow.lineEdit_Manufacturer.setText(idn.split(',')[0])
                #self.MainWindow.lineEdit_Model.setText(idn.split(',')[1])
                #self.MainWindow.lineEdit_SN.setText(idn.split(',')[2])
                #self.MainWindow.lineEdit_SoftVersion.setText(idn.split(',')[3])  
                #self.statusBar().showMessage("Nspec Analyzer for DSO-X4024A",2000)
            return
            #with closing(sock):
            #    sock.connect((host,port))                
            #    sock.send('*RST')
            #return
            self.connection_dsox4024a = 1
        except ():
            print "TCP connection error"
            self.connection_dsox4024a = 0
        
        
    def disconnect_DSOX4024A(self):
        self.statusBar().showMessage("disconnect DSOX4024A", 2000)
        #self.MainWindow.checkBox_labjackT7.setStyleSheet("color: black")                    
        self.connect_dsox4024a = 0
        # Close handle
        print("\n Disconnect DSOX4024A")
        self.inst_dsox4024a.close()
            
    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtGui.QMessageBox.about(self, "About",
"""nspec.py
Copyright 2018 Akio HOSHINO,

This program is noise spectrum generator for Keysight DSOX4024A.
It may be used and modified with no restriction; raw copies as well as
modified versions may be distributed without limitation."""
)

    def nspec_abort(self):
        print 'abort nspec'
        sys.exit()

    def nspec_start(self):
        thr = threading.Thread(target=self.nspec_taskrun)
        thr.start()
        #thr.join()
        #self.plot_psd_avg()        
    def nspec_taskrun(self):
        completed_2k = 0.0
        completed_20k = 0.0
        completed_200k = 0.0
        completed_total = 0.0
        self.tdatetime = datetime.now()                
        print 'start nspec at %s' % str(datetime.now())
        gainscale = self.MainWindow.lineEdit_gainscale.text()
        dataset = np.int(self.MainWindow.lineEdit_dataset.text())
        datalength = np.int(self.MainWindow.lineEdit_datalength.text())
        print dataset,datalength, gainscale
        if self.state_2k_value == 1:
            print "start 2k nspec at %s." % str(datetime.now())
            self.send_command_nspec('./comm/setup_nspec_2k.txt')
            os.system('mkdir -p ./data/%s/2k' % str(self.tdatetime.strftime("%y%m%d%H%M%S")))
            self.read_preamble()
            for i in range(1, dataset+1):            
                os.system('ruby ./dso_5054a/ruby/main_get_waveform.rb %s "2k" %s' % (str(self.MainWindow.lineEdit_IP.text()), str(self.tdatetime.strftime("%y%m%d%H%M%S"))))
                print "2k cycle: %s end at %s." % ( str(i), str(datetime.now() ) )
                self.MainWindow.lineEdit_2k.setText("%s" % str(i))
                completed_2k = np.float( np.float(i) / np.float(dataset) * 100.0 * 0.5)                
                #self.MainWindow.progressBar_2k.setValue(completed_2k)
                time.sleep(3.0)
        if self.state_20k_value == 1:
            print "start 20k nspec at %s." % str(datetime.now())
            self.send_command_nspec('./comm/setup_nspec_20k.txt')
            os.system('mkdir -p ./data/%s/20k' % str(self.tdatetime.strftime("%y%m%d%H%M%S")))
            self.read_preamble()            
            for i in range(1,dataset+1):
                os.system('ruby ./dso_5054a/ruby/main_get_waveform.rb %s "20k" %s' % (str(self.MainWindow.lineEdit_IP.text()), str(self.tdatetime.strftime("%y%m%d%H%M%S"))))
                print "20k cycle: %s end at %s." % ( str(i), str(datetime.now() ) )
                self.MainWindow.lineEdit_20k.setText("%s" % str(i))
                completed_20k = np.float( np.float(i) / np.float(dataset) * 100.0 * 0.5)
                #self.MainWindow.progressBar_20k.setValue(completed_20k)
                time.sleep(3.0)
        if self.state_200k_value == 1:
            print "start 200k nspec at %s." % str(datetime.now())            
            self.send_command_nspec('./comm/setup_nspec_200k.txt')            
            os.system('mkdir -p ./data/%s/200k' % str(self.tdatetime.strftime("%y%m%d%H%M%S")))
            self.read_preamble()            
            for i in range(1,dataset+1):
                os.system('ruby ./dso_5054a/ruby/main_get_waveform.rb %s "200k" %s' % (str(self.MainWindow.lineEdit_IP.text()), str(self.tdatetime.strftime("%y%m%d%H%M%S"))))
                print "200k cycle: %s end at %s." % ( str(i), str(datetime.now() ) )
                self.MainWindow.lineEdit_200k.setText(_translate("MainWindow",str(i), None))
                completed_200k = np.float( np.float(i) / np.float(dataset) * 100 * 0.5 )                
                #self.MainWindow.progressBar_200k.setValue(completed_200k)
                time.sleep(3.0)
        if self.state_manual_value == 1:
            print "start manual nspec at %s." % str(datetime.now())
            os.system('mkdir -p ./data/%s/man' % str(self.tdatetime.strftime("%y%m%d%H%M%S")))
            self.read_preamble()
            for i in range(1,dataset+1):                        
                os.system('ruby ./dso_5054a/ruby/main_get_waveform.rb %s "man" %s' % (str(self.MainWindow.lineEdit_IP.text()), str(self.tdatetime.strftime("%y%m%d%H%M%S"))))
                print "man cycle: %s end at %s." % ( str(i), str(datetime.now() ) )
                self.MainWindow.lineEdit_man.setText("%s" % str(i))
                completed_man = np.float( np.float(i) / np.float(dataset) * 100 * 0.5 )
                #self.MainWindow.progressBar_man.setValue(completed_man)
                time.sleep(3.0)
        if self.state_2k_value == 1:
            self.rdata_2kHz_avg()
            completed_2k = np.float( 100.0 )                
            self.MainWindow.progressBar_2k.setValue(completed_2k)
        if self.state_20k_value == 1:
            self.rdata_20kHz_avg()
            completed_20k = np.float( 100.0 )                
            self.MainWindow.progressBar_20k.setValue(completed_20k)
        if self.state_200k_value == 1:
            self.rdata_200kHz_avg()
            completed_200k = np.float( 100.0 )                
            self.MainWindow.progressBar_200k.setValue(completed_200k)
        if self.state_manual_value == 1:
            self.rdata_man_avg()
            completed_man = np.float( 100.0 )                
            self.MainWindow.progressBar_man.setValue(completed_man)
        self.MainWindow.pushButton_plot.setDisabled(False)
    def state_2k(self):
        if self.state_2k_value == 0:
            self.state_2k_value = 1
            print 'set 2kHz'            
        else:
            self.state_2k_value = 0
            print 'unset 2kHz'
            
    def state_20k(self):
        if self.state_20k_value == 0:
            self.state_20k_value = 1
            print 'set 2kHz'                                
        else:
            self.state_20k_value = 0
            print 'unset 2kHz'
            
    def state_200k(self):
        if self.state_200k_value == 0:        
            self.state_200k_value = 1
            print 'set 200kHz'            
        else:
            self.state_200k_value = 0
            print 'unset 200kHz'
            
    def state_manual(self):
        if self.state_manual_value == 0:        
            self.state_manual_value = 1
            print 'set manualy on hardware'            
        else:
            self.state_manual_value = 0
            print 'unset manual'

    def rdata_man_avg(self):
        self.filelist_man = './data/%s/man/*.dat' % (str(self.tdatetime.strftime("%y%m%d%H%M%S")))
        coef = np.float(self.MainWindow.lineEdit_gainscale.text())
        freq_man = pd.DataFrame({})
        psd_man = pd.DataFrame({})            
        print 'start man'
        files = glob.glob(self.filelist_man)
        print files
        for self.filename in files:
            data = pd.read_csv(str(self.filename),
                               header=None,
                               skiprows=1,
                               sep='\s+',
                               names=['TIME',
                                      'volt',
                                      ],
                               dtype='float64',
                               engine='python'                               
            )
            print self.filename
            dt_man = data['TIME'][1]-data['TIME'][0]
            print 'dt_man = %s s' % str(dt_man)
            interval=np.int(self.MainWindow.lineEdit_datalength.text())
            loopnum=0
            loopid=0
            listv = []
            for i in range(len(data['TIME'])):
                #print " i = " + str(i)
                #print  str(loopnum) + " == " +  str(interval - 1) 
                if ( str(loopnum) == str(interval - 1) ):
                    # Do FFT
                    #print ".....  DO FFT " #+ str(loopnum)
                    freq, real, imag, psd = sxs.scipy_fft(pd.Series(listv)/coef,dt_man)
                    freq_man = pd.concat([freq_man,pd.Series(freq)], axis=1)
                    psd_man = pd.concat([psd_man,pd.Series(psd)], axis=1)
                    # Clear storage
                    loopnum = 0 
                    loopid = loopid + 1 
                    listv = []
                else:
                    # Just store data
                    #print ".....  STORE DATA " + str(loopnum)
                    loopnum=loopnum+1
                    listv.append(data['volt'][i])
            #freq, real, imag, psd = sxs.scipy_fft(data['volt']/coef,dt_man)
            #freq_man = pd.concat([freq_man,pd.Series(freq)], axis=1)
            #psd_man = pd.concat([psd_man,pd.Series(psd)], axis=1)
            data = []            
        self.freq_man_mean = freq_man.mean(axis=1)
        self.psd_man_mean = psd_man.mean(axis=1)
        pd.concat([self.freq_man_mean, self.psd_man_mean],axis=1).to_csv('./data/%s/man/man_mean.csv'  % (str(self.tdatetime.strftime("%y%m%d%H%M%S"))))        
        print self.freq_man_mean
        print self.psd_man_mean
        
    def rdata_200kHz_avg(self):
        self.filelist_200kHz = './data/%s/200k/*.dat' % (str(self.tdatetime.strftime("%y%m%d%H%M%S")))
        coef = np.float(self.MainWindow.lineEdit_gainscale.text())
        freq_200kHz = pd.DataFrame({})
        psd_200kHz = pd.DataFrame({})            
        print 'start 200kHz'
        files = glob.glob(self.filelist_200kHz)
        print files
        for self.filename in files:
            data = pd.read_csv(str(self.filename),
                               header=None,
                               skiprows=1,
                               sep='\s+',
                               names=['TIME',
                                      'volt',
                                      ],
                               dtype='float64',
                               engine='python'                               
            )
            print self.filename
            dt_200kHz = data['TIME'][1]-data['TIME'][0]
            print 'dt_200kHz = %s s' % str(dt_200kHz)
            interval=np.int(self.MainWindow.lineEdit_datalength.text())
            loopnum=0
            loopid=0
            listv = []
            n = 0
            for i in range(len(data['TIME'])):
                #print " i = " + str(i)
                #print  str(loopnum) + " == " +  str(interval - 1) 
                if ( str(loopnum) == str(interval - 1) ):
                    # Do FFT
                    n += 1
                    #print ".....  DO FFT " + str(n)
                    freq, real, imag, psd = sxs.scipy_fft(pd.Series(listv)/coef,dt_200kHz)
                    freq_200kHz = pd.concat([freq_200kHz,pd.Series(freq)], axis=1)
                    psd_200kHz = pd.concat([psd_200kHz,pd.Series(psd)], axis=1)
                    # Clear storage
                    loopnum = 0 
                    loopid = loopid + 1 
                    listv = []
                else:
                    # Just store data
                    #print ".....  STORE DATA " + str(loopnum)
                    loopnum=loopnum+1
                    listv.append(data['volt'][i])
            data = []            
        self.freq_200kHz_mean = freq_200kHz.mean(axis=1)
        self.psd_200kHz_mean = psd_200kHz.mean(axis=1)
        pd.concat([self.freq_200kHz_mean, self.psd_200kHz_mean],axis=1).to_csv('./data/%s/200k/200kHz_mean.csv'  % (str(self.tdatetime.strftime("%y%m%d%H%M%S"))))        
        #print self.freq_200kHz_mean
        #print self.psd_200kHz_mean
        
    def rdata_20kHz_avg(self):
        self.filelist_20kHz = './data/%s/20k/*.dat' % (str(self.tdatetime.strftime("%y%m%d%H%M%S")))        
        coef = np.float(self.MainWindow.lineEdit_gainscale.text())
        freq_20kHz = pd.DataFrame({})
        psd_20kHz = pd.DataFrame({})            
        print 'start 20kHz'
        files = glob.glob(self.filelist_20kHz)
        print files        
        for self.filename in files:
            data = pd.read_csv(str(self.filename),
                               header=None,
                               skiprows=1,
                               sep='\s+',
                               names=['TIME',
                                      'volt'
                               ],
                               dtype='float64',
                               engine='python'                               
            )
            print self.filename
            dt_20kHz = data['TIME'][1]-data['TIME'][0]
            print 'dt_20kHz = %s s' % str(dt_20kHz)
            interval=np.int(self.MainWindow.lineEdit_datalength.text())
            loopnum=0
            loopid=0
            listv = []
            for i in range(len(data['TIME'])):
                #print " i = " + str(i)
                #print  str(loopnum) + " == " +  str(interval - 1) 
                if ( str(loopnum) == str(interval - 1) ):
                    # Do FFT
                    #print ".....  DO FFT " #+ str(loopnum)
                    freq, real, imag, psd = sxs.scipy_fft(pd.Series(listv)/coef,dt_20kHz)
                    freq_20kHz = pd.concat([freq_20kHz,pd.Series(freq)], axis=1)
                    psd_20kHz = pd.concat([psd_20kHz,pd.Series(psd)], axis=1)
                    # Clear storage
                    loopnum = 0 
                    loopid = loopid + 1 
                    listv = []
                else:
                    # Just store data
                    #print ".....  STORE DATA " + str(loopnum)
                    loopnum=loopnum+1
                    listv.append(data['volt'][i])
            data = []
        self.freq_20kHz_mean = freq_20kHz.mean(axis=1).dropna()
        self.psd_20kHz_mean = psd_20kHz.mean(axis=1).dropna()
        pd.concat([self.freq_20kHz_mean, self.psd_20kHz_mean],axis=1).to_csv('./data/%s/20k/20kHz_mean.csv'  % (str(self.tdatetime.strftime("%y%m%d%H%M%S"))))        
        
    def rdata_2kHz_avg(self):
        self.filelist_2kHz = './data/%s/2k/*.dat' % (str(self.tdatetime.strftime("%y%m%d%H%M%S")))                
        coef = np.float(self.MainWindow.lineEdit_gainscale.text())
        interval = np.int(self.MainWindow.lineEdit_datalength.text())        
        freq_2kHz = pd.DataFrame({})
        psd_2kHz = pd.DataFrame({})            
        print 'start 2kHz'
        files = glob.glob(self.filelist_2kHz)
        print files        
        for self.filename in files:
            data = pd.read_csv(str(self.filename),
                               header=None,
                               skiprows=1,
                               sep='  ',
                               names=['TIME',
                                      'volt'
                               ],
                               dtype='float64',
                               engine='python'
            )
            print self.filename
            #print np.float(data['TIME'][1]), np.float(data['TIME'][0])
            dt_2kHz = np.float(data['TIME'][1])-np.float(data['TIME'][0])
            print 'dt_2kHz = %s s' % str(dt_2kHz)
            loopnum=0
            loopid=0
            listv = []
            n = 0
            for i in range(len(data['TIME'])):
                #print " i = " + str(i)
                #print  str(loopnum) + " == " +  str(interval - 1) 
                if ( str(loopnum) == str(interval - 1) ):
                    n += 1
                    # Do FFT
                    #print ".....  DO FFT "  +str(n)
                    freq, real, imag, psd = sxs.scipy_fft(pd.Series(listv)/coef,dt_2kHz)
                    freq_2kHz = pd.concat([freq_2kHz,pd.Series(freq)], axis=1)
                    psd_2kHz = pd.concat([psd_2kHz,pd.Series(psd)], axis=1)
                    # Clear storage
                    loopnum = 0 
                    loopid = loopid + 1 
                    listv = []
                else:
                    # Just store data
                    #print ".....  STORE DATA " + str(loopnum)
                    loopnum=loopnum+1
                    listv.append(data['volt'][i])
            #freq, real, imag, psd = sxs.scipy_fft(data['volt']/coef,dt_2kHz)
            data = []
        self.freq_2kHz_mean = freq_2kHz.mean(axis=1)
        self.psd_2kHz_mean = psd_2kHz.mean(axis=1)
        pd.concat([self.freq_2kHz_mean, self.psd_2kHz_mean],axis=1).to_csv('./data/%s/2k/2kHz_mean.csv'  % (str(self.tdatetime.strftime("%y%m%d%H%M%S"))))                

    def plot_psd_avg(self):
        print "plot_psd_avg"
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        fig.subplots_adjust(top=0.85)
        ax1.set_xlabel('Frequency (Hz)')
        ax1.set_ylabel('PSD (A/$\\sqrt{\\rm Hz}$)')
        if self.state_2k_value == 1:
            ax1.plot(self.freq_2kHz_mean,self.psd_2kHz_mean,label='2kHz')
        if self.state_20k_value == 1:
            ax1.plot(self.freq_20kHz_mean, self.psd_20kHz_mean,label='20kHz')
        if self.state_200k_value == 1:
            ax1.plot(self.freq_200kHz_mean,self.psd_200kHz_mean,label='200kHz')
        if self.state_manual_value == 1:
            ax1.plot(self.freq_man_mean,self.psd_man_mean,label='manual')
        ax1.grid(True)
        #ax1.set_xlim([1e2, 1e5])
        #ax1.set_ylim([1e-9, 1e-2])
        ax1.set_yscale('log')
        ax1.set_xscale('log')
        plt.legend()
        plt.savefig('psd.png', format='png', dpi=100)
        plt.show()
        #plt.pause()
        #plt.clf()


        
if __name__ == '__main__':
    qApp = QtWidgets.QApplication(sys.argv)
    aw = AppWindow_DSOX4024A()
    aw.setWindowTitle( "%s" % progname)
    aw.show()
    sys.exit(qApp.exec_())
