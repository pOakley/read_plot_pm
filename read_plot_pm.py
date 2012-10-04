#Data Format

#Inputs
#   live_data: Set to 1 for reading data off the control box in real time. Set to 0 for reading a previously recorded filename
#   Filename: filename to read if live_data = 0, filename to save if live_data = 1

#Outputs
#   None

#Save files
#   Saves the data in a csv file (using the filename input) if reading data live_data
#   Saves the figure plots (2 of them) regardless of live_data.
#   Note - program will not overwrite existing files

#Things to fix
#   Better interactivity with selecting a USB port
#   Right now the program parses everything into separate variables (x1,y1,x2,y2, etc.) for ease of understand. This is likely inefficient and should be changed later
#   Need the magic code for coordinate transformation
#   Is sys.exit() the proper way to exit a program?

#==========================================Import necessary libraries
#import matplotlib.pyplot as plt

#python -m serial.tools.miniterm --port='/dev/tty.usbserial-FTT3QDXK' --baud=115200

import numpy as np
#from time import sleep

import random

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas


import serial
import serial.tools.list_ports as serports
#import struct
import math
import os.path
import sys
import datetime
import time

from PyQt4 import QtCore, QtGui
import sys

class Position_data():

    def __init__(self, fake_data=False):
        '''Initialize the data'''
        self.fake_data = fake_data
        self.initialize_data()
        if (self.fake_data == False):
            self.connect_to_usb()


    def initialize_data(self):
        '''Initialize data'''

        self.data = []

        self.x1 = []
        self.x1_norm = []
        self.y1 = []
        self.y1_norm = []

        self.x2 = []
        self.x2_norm = []
        self.y2 = []
        self.y2_norm = []

        self.x3 = []
        self.x3_norm = []
        self.y3 = []
        self.y3_norm = []

        self.x4 = []
        self.x4_norm = []
        self.y4 = []
        self.y4_norm = []

        self.byte = []
        self.byte_to_int = []
        self.bit15array = []
        self.valuearray = []

        self.x1_position = []
        self.y1_position = []
        self.position = np.zeros((1,8))


    def connect_to_usb(self):
        '''Connect to USB feed'''

        list_of_usb_ports = serports.comports()

        self.port = '/dev/tty.usbserial-FTT3QDXK'	#Small PCB Converter
        #self.port = '/dev/tty.usbserial-FTT31FFA'	#Bigger Converter
        #self.port = '/dev/tty.usbmodem411'
        self.baudrate = 115200
        self.parity = 'N'
        self.rtscts = False
        self.xonxoff = False
        #self.ser = serial.Serial(self.port, self.baudrate, parity=self.parity, rtscts=self.rtscts, xonxoff=self.xonxoff, timeout=1)
        self.ser = serial.Serial(self.port, self.baudrate)

        print 'Setting up USB connection:'
        print 'Port: ' + self.port
        print 'Baudrate: ' + str(self.baudrate)
        print 'Parity: ' + self.parity
        print 'RTSCTS: ' + str(self.rtscts)
        print 'XONXOFF: ' + str(self.xonxoff)



    def calculate_positions(self):
        '''Calculate laser spot position from diode values'''
        #Calculate spot positions
        self.x1_position = self.valuearray[1] / self.valuearray[0]
        self.y1_position = self.valuearray[3] / self.valuearray[2]
        self.x2_position = self.valuearray[5] / self.valuearray[4]
        self.y2_position = self.valuearray[7] / self.valuearray[6]
        self.x3_position = self.valuearray[9] / self.valuearray[8]
        self.y3_position = self.valuearray[11] / self.valuearray[10]
        self.x4_position = self.valuearray[13] / self.valuearray[12]
        self.y4_position = self.valuearray[15] / self.valuearray[14]

	position_list = [self.x1_position,self.y1_position,self.x2_position,self.y2_position,self.x3_position,self.y3_position,self.x4_position,self.y4_position]

	if np.size(self.position) > 80:
	        self.position = np.zeros((1,8))

	if np.size(self.position) == 8:
		self.position[0,:] = position_list
        else:
        	self.position = np.vstack([self.position,position_list])

    def convert_from_twos_complement(self,value):
        '''Convert from twos complement'''
        #Check whether the input is positive (0 first bit) or negative (1 first bit)
        #if value > 127:
	if value >= (2**13):
		#Zero the sign bit
		#value ^= (1<<13) #was 7
		
		#Add 1
		#value += 1
		
		#Make negative
		#value = -value
		value = ~(value ^ (2**14-1))		

	#print value
        return value



    def sync_feed(self,sync_attempt):
        '''Search for the frame sync byte'''
        while sync_attempt < 100:

            #Read in a byte (will be an ascii character)
            sync_test_byte = self.ser.read(1)

            #Convert byte to integer (needed to perform operations on)
            sync_test_int = ord(sync_test_byte)
            #print sync_test_int

            #Check to see if the first bit is a 1
            #This happens when the overall integer value is >= 128

            if sync_test_int >= 128:
                #print 'Sync in: ' + str(sync_attempt) + ' attempts'
                return sync_test_byte

            sync_attempt += 1

        print 'Failed to sync in: ' + str(sync_attempt) + ' attempts'
        #sys.exit()
        return 0;


    def read_cycle(self):
        '''Reads a full 32 byte cycle'''
        #print time.time()
        sync_attempt=0

        self.cycle_byte = []
        self.cycle_byte_to_int = []

        if (self.fake_data == False):
            self.cycle_byte.append(self.sync_feed(sync_attempt))
            self.cycle_byte_to_int.append(ord(self.cycle_byte[0]))

            if self.cycle_byte_to_int[0] < 128:
                print "Failed to Sync. Exiting"
                #return 0;
                sys.exit()

            self.read_31_bytes()

            self.valuearray = self.cycle_valuearray
            self.bit15array = self.cycle_bit15array
            self.byte = self.cycle_byte
            self.byte_to_int = self.cycle_byte_to_int

            self.calculate_positions()

            self.print_positions()
        else:
            r = random.uniform(-3,3)
            self.x1_position.append(r)
            self.y1_position.append(r)
            if np.size(self.position) == 0:
            	self.position[0,:] = np.ones(8)*r
            else:
            	self.position = np.vstack([self.position,np.ones(8)*r])

        return self.position
        #yield self.position
        #yield [self.x1_position, self.y1_position]

    def read_31_bytes(self):
        '''Read the next 31 bytes'''
        
        self.cycle_bit15array = []
        self.cycle_valuearray = []

        for k in range(1,32):
            self.cycle_byte.append(self.ser.read(1))

            # return an integer representing the Unicode code point of the character
            self.cycle_byte_to_int.append(ord(self.cycle_byte[k]))
            #print ord(self.cycle_byte[k])

            if (k % 2 == 1):

                #Each diode sends 2 bytes worth of data structured as:
                #Frame-sync bit, B13 - B7
                #Frame-sync bit, B6  - B0
                #The data bits (B13 - B0) are arranged MSB - LSB

                #Zero the frame sync
                #(1 << 7) = 00000001 shifted 7 places to the left = 10000000 = 128
                #Looks for common 1s between the variable and the complement of 128 (01111111)
                #In other words the first bit is 0, and all the others are whatever they originally were
                desynced1 = self.cycle_byte_to_int[k-1] & ~(1 << 7)
                desynced2 = self.cycle_byte_to_int[k]   & ~(1 << 7)

                #combine the two bitarrays
                #Combines the first variable (least significant bits) with the second variable (most significant bits)
                #Example: 1010101 | 1111111 = 11111111010101
                self.cycle_bit15array.append(desynced1 | (desynced2 << 7))

                #Put the bits back together and put it into a float variable for easy division
                self.cycle_valuearray.append(float(self.convert_from_twos_complement(self.cycle_bit15array[(k-1)/2])))



    def print_positions(self):
        '''Print out all the variables'''
        print 'Byte original bitarray bitarray bit14array valuearray'
        for printinfo in range(32):
            print printinfo
            if printinfo % 2==0:
                print self.byte[printinfo], '  ', self.byte_to_int[printinfo]

            if printinfo % 2==1:
                print self.byte[printinfo],'   ', self.byte_to_int[printinfo],'   ', self.bit15array[(printinfo-1)/2], '   ', self.valuearray[(printinfo-1)/2]

        print
        print 'Positions'
        print self.x1_position
        print self.y1_position
        print self.x2_position
        print self.y2_position
        print self.x3_position
        print self.y3_position
        print self.x4_position
        print self.y4_position


    def save_data(self):
        '''Save the data'''

        for k in range(8):
        	print str(self.position[-1,k])
        	self.save_file.write(str(self.position[-1,k])+', ')
        
        self.save_file.write('\n')
        
        #current_time = str(datetime.datetime.now())

        #print "Saved Data: ", data_tosave_filename




class Position_plots(QtGui.QMainWindow, FigureCanvas):

	def __init__(self, data):
		'''Initialize the GUI Window'''
		self.ts_old = time.time()
		self.ts = time.time()
		self.main_gui = QtGui.QMainWindow()
		self.setupUi(self.main_gui)
		self.setup_diodes()
		self.x = []
		self.y = []
		self.record = False
		self.retranslateUi(self.main_gui)
		QtCore.QMetaObject.connectSlotsByName(self.main_gui)
		self._timer = self.fig1.canvas.new_timer(interval = 300)
	        self._timer.interval = 23
        	self._timer.add_callback(self.update_display)
        	self._data = data
		self.main_gui.show()
        
        def start(self):
		self._timer.start()		

	def pause(self):
		self._timer.stop()
		
	def record(self):
		if self.record == True:
			try:
				self._data.save_file.close()
			except:
				print "Error closing save file - data may be lost"
			self.record = False
		else:
			try:	
				save_filename = self.filename_box.text()
				print 'trying to open file: ' + save_filename
				write_header = True
				if os.path.isfile(save_filename):
					write_header = False
				self._data.save_file = open(save_filename,'a')
				if write_header:
					self._data.save_file.write("X1, Y1, X2, Y2, X3, Y3, X4, Y4 \n")
			except:
				print "Error opening file to save - data won't be saved"
			self.record = True
			
		
	def zero(self):
		pass

	def setupUi(self, MainWindow):
		MainWindow.setObjectName(_fromUtf8("MainWindow"))
		MainWindow.resize(998, 780)
		self.centralwidget = QtGui.QWidget(MainWindow)
		self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
		self.diode_plot_widget = QtGui.QWidget(self.centralwidget)
		self.diode_plot_widget.setGeometry(QtCore.QRect(29, 39, 671, 571))
		self.diode_plot_widget.setObjectName(_fromUtf8("diode_plot_widget"))
		self.pixel_plot_widget = QtGui.QWidget(self.centralwidget)
		self.pixel_plot_widget.setGeometry(QtCore.QRect(29, 539, 471, 191))
		self.pixel_plot_widget.setObjectName(_fromUtf8("pixel_plot_widget"))
		self.widget = QtGui.QWidget(self.centralwidget)
		self.widget.setGeometry(QtCore.QRect(730, 40, 241, 691))
		self.widget.setObjectName(_fromUtf8("widget"))
		self.verticalLayout_2 = QtGui.QVBoxLayout(self.widget)
		self.verticalLayout_2.setMargin(0)
		self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
		self.datamode_label = QtGui.QLabel(self.widget)
		font = QtGui.QFont()
		font.setPointSize(18)
		font.setBold(True)
		font.setWeight(75)
		self.datamode_label.setFont(font)
		self.datamode_label.setObjectName(_fromUtf8("datamode_label"))
		self.verticalLayout_2.addWidget(self.datamode_label)
		self.verticalLayout = QtGui.QVBoxLayout()
		self.verticalLayout.setSpacing(15)
		self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
		self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
		self.livedata_button = QtGui.QRadioButton(self.widget)
		self.livedata_button.setObjectName(_fromUtf8("livedata_button"))
		self.verticalLayout.addWidget(self.livedata_button)
		self.existingdata_button = QtGui.QRadioButton(self.widget)
		self.existingdata_button.setObjectName(_fromUtf8("existingdata_button"))
		self.verticalLayout.addWidget(self.existingdata_button)
		self.fakedata_button = QtGui.QRadioButton(self.widget)
		self.fakedata_button.setObjectName(_fromUtf8("fakedata_button"))
		self.verticalLayout.addWidget(self.fakedata_button)
		self.verticalLayout_2.addLayout(self.verticalLayout)
		self.line = QtGui.QFrame(self.widget)
		self.line.setFrameShape(QtGui.QFrame.HLine)
		self.line.setFrameShadow(QtGui.QFrame.Sunken)
		self.line.setObjectName(_fromUtf8("line"))
		self.verticalLayout_2.addWidget(self.line)
		self.recorddata_label = QtGui.QLabel(self.widget)
		font = QtGui.QFont()
		font.setPointSize(18)
		font.setBold(True)
		font.setWeight(75)
		self.recorddata_label.setFont(font)
		self.recorddata_label.setObjectName(_fromUtf8("recorddata_label"))
		self.verticalLayout_2.addWidget(self.recorddata_label)
		self.horizontalLayout = QtGui.QHBoxLayout()
		self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
		self.pause_button = QtGui.QToolButton(self.widget)
		self.pause_button.setText(_fromUtf8(""))
		icon = QtGui.QIcon()
		icon.addPixmap(QtGui.QPixmap(_fromUtf8("blue_pause_button.jpeg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.pause_button.setIcon(icon)
		self.pause_button.setIconSize(QtCore.QSize(32, 32))
		self.pause_button.setObjectName(_fromUtf8("pause_button"))
		self.horizontalLayout.addWidget(self.pause_button)
		self.record_button = QtGui.QToolButton(self.widget)
		self.play_button = QtGui.QToolButton(self.widget)
		self.play_button.setText(_fromUtf8(""))
		icon1 = QtGui.QIcon()
		icon1.addPixmap(QtGui.QPixmap(_fromUtf8("blue_play_button.jpeg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.play_button.setIcon(icon1)
		self.play_button.setIconSize(QtCore.QSize(32, 32))
		self.play_button.setObjectName(_fromUtf8("play_button"))
		self.horizontalLayout.addWidget(self.play_button)
		self.record_button.setText(_fromUtf8(""))
		icon2 = QtGui.QIcon()
		icon2.addPixmap(QtGui.QPixmap(_fromUtf8("record_button.gif")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.record_button.setIcon(icon2)
		self.record_button.setIconSize(QtCore.QSize(32, 32))
	        self.record_button.setCheckable(True)
		self.record_button.setObjectName(_fromUtf8("record_button"))
		self.horizontalLayout.addWidget(self.record_button)
		self.verticalLayout_2.addLayout(self.horizontalLayout)
		self.filename_box = QtGui.QLineEdit(self.widget)
		self.filename_box.setObjectName(_fromUtf8("filename_box"))
		self.verticalLayout_2.addWidget(self.filename_box)
		self.line_3 = QtGui.QFrame(self.widget)
		self.line_3.setFrameShape(QtGui.QFrame.HLine)
		self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
		self.line_3.setObjectName(_fromUtf8("line_3"))
		self.verticalLayout_2.addWidget(self.line_3)
		self.zero_button = QtGui.QPushButton(self.widget)
		self.zero_button.setObjectName(_fromUtf8("zero_button"))
		self.verticalLayout_2.addWidget(self.zero_button)
		self.line_2 = QtGui.QFrame(self.widget)
		self.line_2.setFrameShape(QtGui.QFrame.HLine)
		self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
		self.line_2.setObjectName(_fromUtf8("line_2"))
		self.verticalLayout_2.addWidget(self.line_2)
		self.serialport_label = QtGui.QLabel(self.widget)
		font = QtGui.QFont()
		font.setPointSize(18)
		font.setBold(True)
		font.setWeight(75)
		self.serialport_label.setFont(font)
		self.serialport_label.setObjectName(_fromUtf8("serialport_label"))
		self.verticalLayout_2.addWidget(self.serialport_label)
		self.listWidget = QtGui.QListWidget(self.widget)
		self.listWidget.setObjectName(_fromUtf8("listWidget"))
		#item = QtGui.QListWidgetItem()
		#self.listWidget.addItem(item)
		self.verticalLayout_2.addWidget(self.listWidget)
		MainWindow.setCentralWidget(self.centralwidget)
		self.menubar = QtGui.QMenuBar(MainWindow)
		self.menubar.setGeometry(QtCore.QRect(0, 0, 798, 22))
		self.menubar.setObjectName(_fromUtf8("menubar"))
		MainWindow.setMenuBar(self.menubar)
		self.statusbar = QtGui.QStatusBar(MainWindow)
		self.statusbar.setObjectName(_fromUtf8("statusbar"))
		MainWindow.setStatusBar(self.statusbar)
		
		QtCore.QObject.connect(self.play_button, QtCore.SIGNAL(_fromUtf8("clicked()")), self.start)
		QtCore.QObject.connect(self.record_button, QtCore.SIGNAL(_fromUtf8("clicked()")), self.record)
		QtCore.QObject.connect(self.pause_button, QtCore.SIGNAL(_fromUtf8("clicked()")), self.pause)
		QtCore.QObject.connect(self.zero_button, QtCore.SIGNAL(_fromUtf8("clicked()")), self.zero)

		
	def retranslateUi(self, MainWindow):
		MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
		self.datamode_label.setText(QtGui.QApplication.translate("MainWindow", "Data Mode", None, QtGui.QApplication.UnicodeUTF8))
		self.livedata_button.setText(QtGui.QApplication.translate("MainWindow", "Plot Live Data", None, QtGui.QApplication.UnicodeUTF8))
		self.existingdata_button.setText(QtGui.QApplication.translate("MainWindow", "Plot Existing Data", None, QtGui.QApplication.UnicodeUTF8))
		self.fakedata_button.setText(QtGui.QApplication.translate("MainWindow", "Plot Fake Data", None, QtGui.QApplication.UnicodeUTF8))
		self.recorddata_label.setText(QtGui.QApplication.translate("MainWindow", "Record Data", None, QtGui.QApplication.UnicodeUTF8))
		self.pause_button.setToolTip(QtGui.QApplication.translate("MainWindow", "Pause recording", None, QtGui.QApplication.UnicodeUTF8))
		self.record_button.setToolTip(QtGui.QApplication.translate("MainWindow", "Start / resume recording", None, QtGui.QApplication.UnicodeUTF8))
		self.filename_box.setText(QtGui.QApplication.translate("MainWindow", "~/Desktop/", None, QtGui.QApplication.UnicodeUTF8))
		self.zero_button.setText(QtGui.QApplication.translate("MainWindow", "Zero Diodes", None, QtGui.QApplication.UnicodeUTF8))
		self.serialport_label.setText(QtGui.QApplication.translate("MainWindow", "Serial Ports", None, QtGui.QApplication.UnicodeUTF8))
		__sortingEnabled = self.listWidget.isSortingEnabled()
		self.listWidget.setSortingEnabled(False)
		
		list_of_usb_ports = serports.comports()
		#ports = list_of_usb_ports.split(',')
		#print ports
		counter = 0
		for usb_option in list_of_usb_ports:
			usb_option = usb_option[0]
			item = QtGui.QListWidgetItem()
		        self.listWidget.addItem(item)
			item = self.listWidget.item(counter)
			item.setText(QtGui.QApplication.translate("MainWindow", usb_option, None, QtGui.QApplication.UnicodeUTF8))
			counter += 1
		
		self.listWidget.setSortingEnabled(__sortingEnabled)

    #def plot_grid(xcenter,ycenter,angle,color,figure):
	def setup_grid(self):
		'''Plot the initial pixel grid'''
	
		self.xcenter = 1
		self.ycenter = 1
		self.angle = 15/57.3
		self.color = 'r'
	
		pixel_size = .6
		edge = float(6) * pixel_size
		length = pixel_size * 6
	
		xstart1 = range(-6,7)
		xend1 = xstart1
		ystart1 = np.zeros(13) - 6
		yend1 = ystart1 + 12
	
		xstart2 = np.zeros(13) - 6
		xend2 = xstart2 + 12
		ystart2 = range(-6,7)
		yend2 = ystart2
	
		rotation_matrix = [[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]]
	
		for k in range(0,13):
			spot_start1 = [xstart1[k],ystart1[k]]
			spot_end1 = [xend1[k],yend1[k]]
			
			spot_start_transformed1 = np.dot(spot_start1,rotation_matrix)
			spot_end_transformed1 = np.dot(spot_end1,rotation_matrix)
			
			spot_start2 = [xstart2[k],ystart2[k]]
			spot_end2 = [xend2[k],yend2[k]]
			
			spot_start_transformed2 = np.dot(spot_start2,rotation_matrix)
			spot_end_transformed2 = np.dot(spot_end2,rotation_matrix)
			figure.plot([spot_start_transformed1[0],spot_end_transformed1[0]],[spot_start_transformed1[1],spot_end_transformed1[1]],color=color)
			figure.plot([spot_start_transformed2[0],spot_end_transformed2[0]],[spot_start_transformed2[1],spot_end_transformed2[1]],color=color)
			
	
		figure.set_xlim([-10,10])
		figure.set_ylim([-10,10])
		figure.set_title('Pixel Map')


	def setup_diodes(self):
		'''Plot the initial diode maps'''
		self.fig1 = Figure()#plt.figure()
		#self.line1 = Line2D([],[],color='r*')
		self.canvas = FigureCanvas(self.fig1)
		self.canvas.setParent(self.diode_plot_widget)
			
		self.diode1 = self.fig1.add_subplot(2,2,1)
		self.diode1_plot = self.diode1.plot(0, 0,'k.')       
		self.diode1.set_xlabel('X Position [mm]')
		self.diode1.set_ylabel('X Position [mm]')
		self.diode1.set_title('Diode 1')
	
		self.diode2 = self.fig1.add_subplot(2,2,2)
		self.diode2_plot = self.diode2.plot(0, 0,'k.')	
		self.diode2.set_xlabel('X Position [mm]')
		self.diode2.set_ylabel('X Position [mm]')
		self.diode2.set_title('Diode 2')
		
		self.diode3 = self.fig1.add_subplot(2,2,3)
		self.diode3_plot = self.diode3.plot(0, 0,'k.')	
		self.diode3.set_xlabel('X Position [mm]')
		self.diode3.set_ylabel('X Position [mm]')
		self.diode3.set_title('Diode 3')
		
		self.diode4 = self.fig1.add_subplot(2,2,4)
		self.diode4_plot = self.diode4.plot(0, 0,'k.')	
		self.diode4.set_xlabel('X Position [mm]')
		self.diode4.set_ylabel('X Position [mm]')
		self.diode4.set_title('Diode 4')
			
	
	
		
	
	
		datasize=0
		if (datasize==0):
			self.diode1.set_xlim([-5,5])
			self.diode1.set_ylim([-5,5])
			self.diode2.set_xlim([-5,5])
			self.diode2.set_ylim([-5,5])
			self.diode3.set_xlim([-5,5])
			self.diode3.set_ylim([-5,5])
			self.diode4.set_xlim([-5,5])
			self.diode4.set_ylim([-5,5])
	
		#self.fig1.show()
	#         self.diode1.figure.canvas.draw()
	#         self.diode2.figure.canvas.draw()
	#         self.diode3.figure.canvas.draw()
	#         self.diode4.figure.canvas.draw()
	
		#self.draw()
		#plt.show()
		self.canvas.draw()
	
	def update_display(self):
		'''Update the plot windows'''
		#self.update_grid(data)
		#print newdata
		self.update_diodes()
		if self.record:
			self._data.save_data()
		#return a
	
	def update_grid(self, data):
		'''Update the pixel grid'''


	def update_diodes(self):
		'''Update the diode maps'''
		self.ts = time.time()
		print(self.ts - self.ts_old)
		self.ts_old = self.ts

		#x1 = newdata[0][:]
		#y1 = newdata[1][:]
		#print x1
		#print y1
		#self.line1.set_data(x1,y1)
		#self.x.append(newdata[0])
		#self.y.append(newdata[1])
		self._data.fake_data = self.fakedata_button.isChecked()
		data = self._data.read_cycle()
		self.diode1_plot[0].set_data(data[:,0], data[:,1])
		self.diode2_plot[0].set_data(data[:,2], data[:,3])
		self.diode3_plot[0].set_data(data[:,4], data[:,5])
		self.diode4_plot[0].set_data(data[:,6], data[:,7])
		#self.diode4.set_ylim([-5,random.random()*5])
		#self.diode1.figure.set_data(newdata[0],newdata[1])
		#self.diode1.plot(newdata[0],newdata[1],'k.')
		#self.diode2.plot(newdata[2],newdata[3],'k.')
		#self.diode3.plot(newdata[4],newdata[5],'k.')
		#self.diode4.plot(newdata[6],newdata[7],'k.')
	
		#self.diode1.figure.canvas.draw()
		#self.fig1.canvas.draw()
		
		#return self.line1
		self.canvas.draw()
		#self.main_gui.show()
	


if __name__ == "__main__":
    #==========================================Setup Parameters
    
	try:
		_fromUtf8 = QtCore.QString.fromUtf8
	except AttributeError:
		_fromUtf8 = lambda s: s
	
	#Create class instances
	#plt.ion()
	
	data    = Position_data(fake_data=True)
	#display = Position_plots()
	
	sync_attempt = 0
	read_cycle = 1
	
	#Using the Position Plots Class fig1, get data from the Position Data class (read_cycle function)
	#and display it using the Position Plots class (update_display function)
	#Do this every X milliseconds
	#ani = animation.FuncAnimation(display.fig1, display.update_display, data.read_cycle, interval=1000, blit=True)
	
	app = QtGui.QApplication(sys.argv)
	display=Position_plots(data)
	#display.show()
	
	#plt.draw()
	#print 'poop'
	#for read_times in range(10):
	#	display.update_display(data.read_cycle())
	#	time.sleep(.2)
		
	#Animation doesn't happen without this
	
	
	sys.exit(app.exec_())
