
#python -m serial.tools.miniterm --port='/dev/tty.usbserial-FTT3QDXK' --baud=115200
#python -m serial.tools.miniterm --port='/dev/tty.SLAB_USBtoUART' --baud=115200

import numpy as np

import random

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas


import serial
import serial.tools.list_ports as serports
import math
import os.path
import sys
import datetime
import time

from PyQt4 import QtCore, QtGui
import sys

import threading
import Queue


class Diode():
	
	def __init__(self,x,y):
		'''Initialize the diode'''
		#Define the location of the diode based on the CAD model
		#X and Y are in the diode frame
		self.xcenter = x
		self.ycenter = y
		
		
		

class Position_data(threading.Thread):
	

	def __init__(self, buffer):
		'''Initialize the data'''
		
		threading.Thread.__init__(self)
		self._buffer = buffer
		#Count how much data gets put into the buffer
		self.data_stored_counter = 0
		self.daemon = True
		
		self.initialize_data()
		self.num_records = 0
		self.connected_to_usb = False
		
		#THIS IS TEMPORARY - MAKE SURE TO DELETE THIS.
		#RIGHT NOW THIS THREAD STARTS BEFORE IT KNOWS WHETHTER THE DATA IS FAKE OR NOT
		#THAT DETERMINATION DOESN'T HAPPEN UNTIL THE MATPLOTLIB TIMER LOOP OCCURS
		#NEED TO FIX THIS
		self.fake_data = True

		self.record = False

		self.timestart = 0.0
		self.timeend = 0.0
	
	def run(self):
		"""Loop that runs while thread is active"""
		while(True):
			while (self.store_data == True):

				self.read_cycle()

				#timestart = time.time()
				self.move_data_to_buffer()
				#timeend = time.time()
				#print 'putting time ' + str(timeend-timestart)

				if self.record:
					self.save_data()
				time.sleep(.01)


				# print poo
				# poo += 1


	def move_data_to_buffer(self):
		"""Take the new data and put it into the buffer"""
		
		#Update a data stored counter
		# self.new_data_size += 1
		# self.data_stored_counter += self.new_data_size
		

		#Put the data into the buffer
		#self._buffer.put_nowait(self.position)
		self._buffer.put(self.position, False)
		# print "Put the following data into the buffer:"
		# print self.position
			
	def initialize_data(self):
		'''Initialize data'''
	
		#self.data = []
		self.data_timestamp = []
		
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
		self.x2_position = []
		self.y2_position = []
		self.x3_position = []
		self.y3_position = []
		self.x4_position = []
		self.y4_position = []
		
		self.position = np.zeros((1,8))
		self.new_position = np.zeros((1,8))
		self.zero_spot = np.zeros((1,8))

		

	def connect_to_usb(self):
		'''Connect to USB feed'''
	
		#list_of_usb_ports = serports.comports()
	
		#self.port = '/dev/tty.usbserial-FTT3QDXK'	#Small PCB Converter		
		#self.port = '/dev/tty.usbserial-FTT31FFA'	#Bigger Converter

		self.baudrate = 115200
		self.parity = 'N'
		self.rtscts = False
		self.xonxoff = False
		self.dsrdtr = False
		
		self.port = str(self.port)

		try:
			self.ser = serial.Serial(self.port, self.baudrate, rtscts=self.rtscts, xonxoff=self.xonxoff, dsrdtr=self.dsrdtr)
			print 'Setting up USB connection:'
			print 'Port: ' + self.port
			print 'Baudrate: ' + str(self.baudrate)
			print 'Parity: ' + self.parity
			print 'RTSCTS: ' + str(self.rtscts)
			print 'XONXOFF: ' + str(self.xonxoff)    
			self.connected_to_usb = True
			print 'Made USB connection'
		except:
			print "Failed to make USB Connection"





	def calculate_positions(self):
		'''Calculate laser spot position from diode values'''
		#Calculate spot positions
		
		self.voltage_to_position_conversion = 2.5
		
		try:
			self.x1_position = self.valuearray[1] / self.valuearray[0] * self.voltage_to_position_conversion
			self.y1_position = self.valuearray[3] / self.valuearray[2] * self.voltage_to_position_conversion
			self.x2_position = self.valuearray[5] / self.valuearray[4] * self.voltage_to_position_conversion
			self.y2_position = self.valuearray[7] / self.valuearray[6] * self.voltage_to_position_conversion
			self.x3_position = self.valuearray[9] / self.valuearray[8] * self.voltage_to_position_conversion
			self.y3_position = self.valuearray[11] / self.valuearray[10] * self.voltage_to_position_conversion
			self.x4_position = self.valuearray[13] / self.valuearray[12] * self.voltage_to_position_conversion
			self.y4_position = self.valuearray[15] / self.valuearray[14] * self.voltage_to_position_conversion
		except:
			print "ERROR CALCULATING POSITIONS - USUALLY A DIVIDE BY 0"
			print sys.exc_info()[0]	
			
			
		position_list = [self.x1_position,self.y1_position,self.x2_position,self.y2_position,self.x3_position,self.y3_position,self.x4_position,self.y4_position]
	
		#if np.size(self.position) > 80:
		#	self.position = np.zeros((1,8))
		
		#Stupid stuff to handle arrays. Probably should find a smarter way to do this
		if (np.size(self.position) == 8 and np.sum(self.position) == 0.0):
			self.position[0,:] = position_list
		else:
			self.position = np.vstack([self.position,position_list])
		
		#Save time stamps
		self.data_timestamp.append(time.time())

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
				print 'Sync in: ' + str(sync_attempt) + ' attempts'
				return sync_test_byte
			
			sync_attempt += 1
	
		print 'Failed to sync in: ' + str(sync_attempt) + ' attempts'
		#sys.exit()
		return 0;


	def read_cycle(self):
		'''Reads a full 32 byte cycle'''
		sync_attempt=0
	
		self.cycle_byte = []
		self.cycle_byte_to_int = []
	
		if (self.fake_data == False):
		
			   
			if self.connected_to_usb == False:
				self.connect_to_usb()
			
			
			
			if self.connected_to_usb == True:
				#Dump all the backlog
				#print 'Dump size = ' + str(self.ser.inWaiting()/32*32)
				#dump = self.ser.read(self.ser.inWaiting()/32*32)
				self.cycle_byte.append(self.sync_feed(sync_attempt))
				#print "SYNC BYTE"
				#print self.cycle_byte[-1]
				#print ord(self.cycle_byte[-1])
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
				
				#self.print_positions()
				
				#Dump all the backlog
				#print self.ser.inWaiting()
				dump_fudge = 5 #inWaiting() doesn't provide the full buffer size, so need a fudge factor
				print 'Dump size = ' + str(dump_fudge*32 + self.ser.inWaiting()/32*32)
				dump = self.ser.read(dump_fudge*32 + self.ser.inWaiting()/32*32)
						

			
		else:
			r = np.zeros(8)
			for k in range(8):
				r[k] = random.uniform(-3,3)

			#Update the new data. This is what will get saved to file (since the rest is already written)
			# if self.new_data_size==1:
			# 	self.new_position[0,:] = r
			# else:
			# 	self.new_position = np.vstack([self.new_position,r])

			#Update the arrays holding all the data
			if (np.size(self.position) == 8 and np.sum(self.position) == 0.0):
				self.position[0,:] = r
			else:
				self.position = np.vstack([self.position,r])



			self.data_timestamp.append(time.time())
			
	def read_31_bytes(self):
		'''Read the next 31 bytes'''
		
		self.cycle_bit15array = []
		self.cycle_valuearray = []
		print "IN WAITING " + str(self.ser.inWaiting())
		
		self.cycle31_bytes = self.ser.read(31)
		#self.cycle_byte.extend(self.cycle31_bytes)
		
		for k in range(1,32):
			self.cycle_byte.append(self.cycle31_bytes[k-1])

			# return an integer representing the Unicode code point of the character
			#self.cycle_byte_to_int.append(ord(self.cycle_byte[k]))
			self.cycle_byte_to_int.append(ord(self.cycle_byte[-1]))
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
				
				#THIS IS WRONG (10.30.2012)
					#Combines the first variable (least significant bits) with the second variable (most significant bits)
					#Example: 1010101 | 1111111 = 11111111010101
					#self.cycle_bit15array.append(desynced1 | (desynced2 << 7))

				#THIS IS RIGHT (I HOPE) (10.30.2012)
				self.cycle_bit15array.append(desynced2 | (desynced1 << 7))
					
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
		
		#current_time = str(datetime.datetime.now())
		#Time since Jan 1, 1970 (verify with: time.gmtime(0))
		#current_time = str(time.time())
		# print self.new_data_size
		# print np.size(self.data_timestamp)

		try:
			self.timestart = time.time()
			print 'saving time ' + str(self.timeend-self.timestart)
			self.timeend = time.time()
		except:
			print 'first save'

		try:
			self.save_file.write(str(self.data_timestamp[-1]) + ', ')
			for k in range(8):
				self.save_file.write(str(self.position[-1,k]))
				if k < 7:
					self.save_file.write(', ')
			
			self.save_file.write('\n')
			self.num_records += 1
		except:
			print "Error in save loop - data probably not saved"



class Position_plots(QtGui.QMainWindow, FigureCanvas):

	def __init__(self, data, buffer):
		'''Initialize the GUI Window'''

		#Timing information
		self.ts_old = time.time()
		self.ts = time.time()

		#Give this class access to the serial data class
		self._data = data

		#Give this class access to the data buffer
		self._buffer = buffer

		self.retrieved_data = np.zeros((1,8))

		#GUI stuff
		self.main_gui = QtGui.QMainWindow()
		self.setupUi(self.main_gui)

		#Plot stuff
		self.setup_diodes()
		self.setup_grid()

		#More GUI stuff
		self._data.record = False
		self.playing = False
		self.retranslateUi(self.main_gui)
		QtCore.QMetaObject.connectSlotsByName(self.main_gui)

		#Define the plot timer that updates the diodes / map
		self._timer = self.fig1.canvas.new_timer()
		self._timer.interval = 110
		self._timer.add_callback(self.update_display)

		#Color stuff (doesn't work right now)
		self._color_wheel = ['k','r','b','g','m']
		self._color_index = 0

		#Setup the diodes
		self.diode1 = Diode(0,0)
		self.diode2 = Diode(1,1)
		self.diode3 = Diode(2,2)
		self.diode4 = Diode(3,3)

		#Show the GUI
		self.main_gui.show()
        

	def setupUi(self, MainWindow):
		'''Setup the GUI window'''
		MainWindow.setObjectName(_fromUtf8("MainWindow"))
		MainWindow.resize(998, 780)
		self.centralwidget = QtGui.QWidget(MainWindow)
		self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
		self.diode_plot_widget = QtGui.QWidget(self.centralwidget)
		self.diode_plot_widget.setGeometry(QtCore.QRect(30, 40, 671, 571))
		self.diode_plot_widget.setObjectName(_fromUtf8("diode_plot_widget"))
		self.pixel_plot_widget = QtGui.QWidget(self.centralwidget)
		self.pixel_plot_widget.setGeometry(QtCore.QRect(30, 539, 671, 200))
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
		self.livedata_button.setChecked(True)
		self.verticalLayout.addWidget(self.livedata_button)
		self.existingdata_button = QtGui.QRadioButton(self.widget)
		self.existingdata_button.setObjectName(_fromUtf8("existingdata_button"))
		self.verticalLayout.addWidget(self.existingdata_button)
		self.fakedata_button = QtGui.QRadioButton(self.widget)
		self.fakedata_button.setChecked(False)
		self.fakedata_button.setObjectName(_fromUtf8("fakedata_button"))
		self.verticalLayout.addWidget(self.fakedata_button)
		self.realtime_plot_checkbox = QtGui.QCheckBox("Plot realtime data", self.widget)
		self.realtime_plot_checkbox.setChecked(True)
		self.verticalLayout.addWidget(self.realtime_plot_checkbox)
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
		self.play_button = QtGui.QToolButton(self.widget)
		self.play_button.setText(_fromUtf8(""))
		icon1 = QtGui.QIcon()
		icon1.addPixmap(QtGui.QPixmap(_fromUtf8("blue_play_button.jpeg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.play_button.setIcon(icon1)
		self.play_button.setCheckable(True)
		self.play_button.setIconSize(QtCore.QSize(32, 32))
		self.play_button.setObjectName(_fromUtf8("play_button"))
		self.horizontalLayout.addWidget(self.play_button)
		self.record_button = QtGui.QToolButton(self.widget)
		self.record_button.setText(_fromUtf8(""))
		icon2 = QtGui.QIcon()
		icon2.addPixmap(QtGui.QPixmap(_fromUtf8("record_button.gif")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.record_button.setIcon(icon2)
		self.record_button.setIconSize(QtCore.QSize(32, 32))
		self.record_button.setCheckable(True)
		self.record_button.setAutoExclusive(False)
		self.record_button.setAutoRaise(False)
		self.record_button.setArrowType(QtCore.Qt.NoArrow)
		self.record_button.setObjectName(_fromUtf8("record_button"))
		self.horizontalLayout.addWidget(self.record_button)
		self.verticalLayout_2.addLayout(self.horizontalLayout)
		self.filename_box = QtGui.QLineEdit(self.widget)
		self.filename_box.setObjectName(_fromUtf8("filename_box"))
		self.verticalLayout_2.addWidget(self.filename_box)
		self.filename_button = QtGui.QPushButton(self.widget)
		self.filename_button.setObjectName(_fromUtf8("filename_button"))
		self.verticalLayout_2.addWidget(self.filename_button)
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
		item = QtGui.QListWidgetItem()
		self.listWidget.addItem(item)
		item = QtGui.QListWidgetItem()
		self.listWidget.addItem(item)
		self.verticalLayout_2.addWidget(self.listWidget)
		self.data_speed_label = QtGui.QLabel(self.widget)
		font = QtGui.QFont()
		font.setPointSize(18)
		font.setBold(True)
		font.setWeight(75)
		self.data_speed_label.setFont(font)
		self.data_speed_label.setObjectName(_fromUtf8("data_speed_label"))
		self.verticalLayout_2.addWidget(self.data_speed_label)
		self.num_records_label = QtGui.QLabel(self.widget)
		font = QtGui.QFont()
		font.setPointSize(18)
		font.setBold(True)
		font.setWeight(75)
		self.num_records_label.setFont(font)
		self.num_records_label.setObjectName(_fromUtf8("num_records_label"))
		self.verticalLayout_2.addWidget(self.num_records_label)
		self.clearplot_button = QtGui.QPushButton(self.widget)
		self.clearplot_button.setObjectName(_fromUtf8("clearplot_button"))
		self.verticalLayout_2.addWidget(self.clearplot_button)
		MainWindow.setCentralWidget(self.centralwidget)
		self.statusbar = QtGui.QStatusBar(MainWindow)
		self.statusbar.setObjectName(_fromUtf8("statusbar"))
		MainWindow.setStatusBar(self.statusbar)
		
		#Setup the menu system
		self.menubar = QtGui.QMenuBar(MainWindow)
		self.menubar.setGeometry(QtCore.QRect(0, 0, 998, 22))
		self.menubar.setObjectName(_fromUtf8("menubar"))
		self.menuFile = QtGui.QMenu(self.menubar)
		self.menuFile.setObjectName(_fromUtf8("menuFile"))
		MainWindow.setMenuBar(self.menubar)
		# self.actionEmergency_Save_All = QtGui.QAction(MainWindow)
		# self.actionEmergency_Save_All.setObjectName(_fromUtf8("actionEmergency_Save_All"))
		# self.menuFile.addAction(self.actionEmergency_Save_All)
		# self.menubar.addAction(self.menuFile.menuAction())

		#Connect actions with the functions they call
	    #QtCore.QObject.connect(self.actionEmergency_Save_All, QtCore.SIGNAL(_fromUtf8("triggered()")), self.emergency_save)
		QtCore.QObject.connect(self.play_button, QtCore.SIGNAL(_fromUtf8("clicked()")), self.startstop)
		QtCore.QObject.connect(self.record_button, QtCore.SIGNAL(_fromUtf8("clicked()")), self.record)
		QtCore.QObject.connect(self.filename_button, QtCore.SIGNAL(_fromUtf8("clicked()")), self.specify_filename)
		QtCore.QObject.connect(self.clearplot_button, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clear_plot)
		QtCore.QObject.connect(self.realtime_plot_checkbox, QtCore.SIGNAL(_fromUtf8("stateChanged(int)")), self.change_record_speed)

	def retranslateUi(self, MainWindow):
		'''Finish setting up the GUI'''
		MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Micro-X Position Diode Aquisition Tool", None, QtGui.QApplication.UnicodeUTF8))
		self.datamode_label.setText(QtGui.QApplication.translate("MainWindow", "Data Mode", None, QtGui.QApplication.UnicodeUTF8))
		self.livedata_button.setText(QtGui.QApplication.translate("MainWindow", "Live Data", None, QtGui.QApplication.UnicodeUTF8))
		self.existingdata_button.setText(QtGui.QApplication.translate("MainWindow", "Existing Data", None, QtGui.QApplication.UnicodeUTF8))
		self.fakedata_button.setText(QtGui.QApplication.translate("MainWindow", "Test Data", None, QtGui.QApplication.UnicodeUTF8))
		self.recorddata_label.setText(QtGui.QApplication.translate("MainWindow", "Record Data", None, QtGui.QApplication.UnicodeUTF8))
		self.record_button.setToolTip(QtGui.QApplication.translate("MainWindow", "Start / resume recording", None, QtGui.QApplication.UnicodeUTF8))
		self.filename_box.setText(QtGui.QApplication.translate("MainWindow", "/Users/Oakley/Desktop/deleteme.txt", None, QtGui.QApplication.UnicodeUTF8))
		self.filename_button.setText(QtGui.QApplication.translate("MainWindow", "Specify Filename", None, QtGui.QApplication.UnicodeUTF8))
		self.clearplot_button.setText(QtGui.QApplication.translate("MainWindow", "Clear Plots", None, QtGui.QApplication.UnicodeUTF8))
		self.serialport_label.setText(QtGui.QApplication.translate("MainWindow", "Serial Ports", None, QtGui.QApplication.UnicodeUTF8))
		self.data_speed_label.setText(QtGui.QApplication.translate("MainWindow", "Data Rate = 0 Hz", None, QtGui.QApplication.UnicodeUTF8))
		self.num_records_label.setText(QtGui.QApplication.translate("MainWindow", "Records Stored = 0", None, QtGui.QApplication.UnicodeUTF8))

		
		__sortingEnabled = self.listWidget.isSortingEnabled()
		self.listWidget.setSortingEnabled(False)
		self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
		#self.actionEmergency_Save_All.setText(QtGui.QApplication.translate("MainWindow", "Emergency Save All", None, QtGui.QApplication.UnicodeUTF8))

		list_of_usb_ports = serports.comports()

		counter = 0
		for usb_option in list_of_usb_ports:
			usb_option = usb_option[0]
			item = QtGui.QListWidgetItem()
		        self.listWidget.addItem(item)
			item = self.listWidget.item(counter)
			item.setText(QtGui.QApplication.translate("MainWindow", usb_option, None, QtGui.QApplication.UnicodeUTF8))
			counter += 1
		self.listWidget.item(counter-1).setSelected(True)
		self.listWidget.setSortingEnabled(__sortingEnabled)

	def startstop(self):
		'''Start or stop the data taking'''
		if self.playing == False:
			if self._data.record == False:
				self.statusbar.showMessage("Monitoring Diodes")
			else:
				self.statusbar.showMessage("Monitoring Diodes - Recording data to: " + self.save_filename)

			#Start the plotting timer
			self._timer.start()

			#Start the reading thread
			self._data.store_data = True

			if not self._data.isAlive():
				self._data.start()		
				self.playing = True
		else:
			self.statusbar.showMessage("Monitoring Paused")

			#Stop the plotting timer
			self._timer.stop()

			#stop the reading thread
			self.playing = False
			self._data.store_data = False
			
	def change_record_speed(self):
		'''Change the speed of the data taking depending on if plots are generated'''
		if self.realtime_plot_checkbox.isChecked():
			#Slow speed so the plots have time to draw
			self._timer.interval = 110
		else:
			#Fast speed since there's no need for plotting
			self._timer.interval = 110#11
	
	def clear_plot(self):
		'''Clear the plots'''
		
		#Clear all the stored data
		self._data.initialize_data()
		
		#Clear the diode plots
		self.diode1_plot[0].set_data(self._data.position[:,0], self._data.position[:,1])
		self.diode2_plot[0].set_data(self._data.position[:,2], self._data.position[:,3])
		self.diode3_plot[0].set_data(self._data.position[:,4], self._data.position[:,5])
		self.diode4_plot[0].set_data(self._data.position[:,6], self._data.position[:,7])


		#Redisplay the plots		
		self.canvas.draw()

		#Clear the pixel map plot
		self.pixel_plot_new[0].set_data(self.xgrid,self.ygrid)
		self.pixel_plot[0].set_data(self.xgrid,self.ygrid)
		
		#Plot the two grids
		self.canvas2.draw()		
					
	def record(self):
		'''Start or stop recording data'''
		if self._data.record == True:
			#Data is already recording, turn recording off

			#Stop recording
			self._data.record = False
			
			try:
				#Close the save file
				self._data.save_file.close()
				self.statusbar.showMessage("Data saved to file: " + self.save_filename)

			except:
				self.statusbar.showMessage("Error closing save file - data may be lost")
		else:
			#Start recording
			self._data.record = True
			try:
				#Determine the save filename from the filename_box	
				self.save_filename = self.filename_box.text()
				
				#Should we write the header line in the file (line 1)?
				write_header = True

				if os.path.isfile(self.save_filename):
					#File already exists, don't need the header line
					write_header = False
				#Open the file to save to
				self._data.save_file = open(self.save_filename,'a')
				
				#Write the header if a new file
				if write_header:
					self._data.save_file.write("Time [seconds since Jan 1, 1970], X1 [mm], Y1 [mm], X2 [mm], Y2 [mm], X3 [mm], Y3 [mm], X4 [mm], Y4 [mm] \n")
				self.statusbar.showMessage("Opened file for writing: " + self.save_filename)
			except:
				self.statusbar.showMessage("Error opening file to save - data won't be saved")
			
		
	def specify_filename(self, normal = True):
		'''Determine the filename for the save file'''
		fname = QtGui.QFileDialog.getSaveFileName(caption="Select filename to record data to", directory="/Users/Oakley/Desktop/")

		#Add the .txt extension if it's not already there
		if fname[-4:] != ".txt":
			fname += ".txt"
			
		if normal:
			self.filename_box.setText(fname)
		else:
			return fname
		#Advance the color wheel
		#self._color_index += 1
		
		#Find the new zero point from the data class
		#self._data.zero_diodes()

		
	def setup_diodes(self):
		'''Plot the initial diode maps'''
		self.fig1 = Figure()#plt.figure()
		#self.line1 = Line2D([],[],color='r*')
		self.canvas = FigureCanvas(self.fig1)
		self.canvas.setParent(self.diode_plot_widget)
			
		self.diode1 = self.fig1.add_subplot(2,2,1)
		self.diode1_plot = self.diode1.plot(0, 0,'k.')       
		#self.diode1.set_xlabel('X Position [mm]')
		self.diode1.set_ylabel('Y Position [mm]')
		self.diode1.set_title('Diode 1')
	
		self.diode2 = self.fig1.add_subplot(2,2,2)
		self.diode2_plot = self.diode2.plot(0, 0,'k.')	
		#self.diode2.set_xlabel('X Position [mm]')
		#self.diode2.set_ylabel('Y Position [mm]')
		self.diode2.set_title('Diode 2')
		
		self.diode3 = self.fig1.add_subplot(2,2,3)
		self.diode3_plot = self.diode3.plot(0, 0,'k.')	
		self.diode3.set_xlabel('X Position [mm]')
		self.diode3.set_ylabel('Y Position [mm]')
		self.diode3.set_title('Diode 3')
		
		self.diode4 = self.fig1.add_subplot(2,2,4)
		self.diode4_plot = self.diode4.plot(0, 0,'k.')	
		self.diode4.set_xlabel('X Position [mm]')
		#self.diode4.set_ylabel('Y Position [mm]')
		self.diode4.set_title('Diode 4')

	
	
		#Set the limits on the diode plots
		self.diode1.set_xlim([-5,5])
		self.diode1.set_ylim([-5,5])
		self.diode2.set_xlim([-5,5])
		self.diode2.set_ylim([-5,5])
		self.diode3.set_xlim([-5,5])
		self.diode3.set_ylim([-5,5])
		self.diode4.set_xlim([-5,5])
		self.diode4.set_ylim([-5,5])
	
		self.canvas.draw()

	def setup_grid(self):
		'''Set up the figure for plotting the pixel grid'''
		
		#Set up the figures / plots
		self.fig2 = Figure()
		self.fig2.set_size_inches(8,2.5)
		self.canvas2 = FigureCanvas(self.fig2)
		self.canvas2.setParent(self.pixel_plot_widget)
		self.pixel_map = self.fig2.add_subplot(111)
		
		self.pixel_plot_new = self.pixel_map.plot(0,0,color='r')
		self.pixel_plot = self.pixel_map.plot(0,0,color='k')
		
		#Determine values for grid
		self.initialize_grid_values()
		
		#Actually plot the grid
		self.update_grid(0,0,0,'r')
		
		self.pixel_map.set_xlim([-10,10])
		self.pixel_map.set_ylim([-10,10])
		self.pixel_map.set_title('Pixel Map (APPROXIMATION ONLY!)')


	def initialize_grid_values(self):
		'''Initialize the pixel grid'''

		xgrid = []
		ygrid = []
		
		for k in range(6,-1,-1):
			
			x_addition = np.concatenate((np.arange(-6,7),np.arange(-6,7)[::-1]))
			xgrid = np.concatenate((xgrid, x_addition))
			y_addition = np.concatenate((np.ones(13)*k,np.ones(13)*(k-6)))
			ygrid = np.concatenate((ygrid,y_addition))
			
		for k in range(-6,1,1):
			x_addition = np.concatenate((np.ones(13)*k,np.ones(13)*(k+6)))
			xgrid = np.concatenate((xgrid, x_addition))
			y_addition = np.concatenate((np.arange(-6,7),np.arange(-6,7)[::-1]))
			ygrid = np.concatenate((ygrid, y_addition))

		self.xgrid = xgrid
		self.ygrid = ygrid
	
	def update_display(self):
		'''Update the plot windows'''
		
		#This function is called by the matplotlib timer event. So every X milliseconds it gets called automatically

		#Update the diode plots
		self.update_diodes()
		
		#Calculate how much the pixel map has shifted
		self.calculate_shift()
		
		#Update the pixel grid display plot
		self.update_grid(random.uniform(-3,3),random.uniform(-3,3),random.uniform(-3,3),'k')
		

		
	def update_diodes(self):
		'''Update the diode maps'''


		#Determine whether data should be real or fake
		self._data.fake_data = self.fakedata_button.isChecked()
		#This is sort of weird way to find the selected port. Other methods seem to fail though
		#The port will be auto-selected, but doesn't react the same as user-selected.
		#Weird
		selected_ports = self.listWidget.selectedItems()
		self._data.port = str(selected_ports[0].text())
		
		#Obtain data from the queue
		self.retrieve_queue()

		#Timing information
		self.ts = time.time()
		self.data_speed_label.setText(QtGui.QApplication.translate("MainWindow", "Data Rate = " + str(round(self.new_data_size / (self.ts-self.ts_old),1)) + " Hz", None, QtGui.QApplication.UnicodeUTF8))
		self.ts_old = self.ts
		
		#Update labels
		#NOTE THAT THIS WILL NEVER BE EXACTLY RIGHT - THE READING THREAD ADDS MORE RECORDS BETWEEN THE TIME THIS COMMAND IS ISSUED EACH MATPLOTLIB TIMER EVENT
		self.num_records_label.setText(QtGui.QApplication.translate("MainWindow", "Records Stored = " + str(self._data.num_records), None, QtGui.QApplication.UnicodeUTF8))

		#Reposition the new data with respect to the zero point
		#plot_data = data - self._data.zero_spot
		#spot_color = self._color_wheel[self._color_index]
		#self.diode1_plot[0].set_color(spot_color)
		
		if self.realtime_plot_checkbox.isChecked():
			#This is the old stuff, before I made seperate threads
			# self.diode1_plot[0].set_data(self._data.position[:,0], self._data.position[:,1])
			# self.diode2_plot[0].set_data(self._data.position[:,2], self._data.position[:,3])
			# self.diode3_plot[0].set_data(self._data.position[:,4], self._data.position[:,5])
			# self.diode4_plot[0].set_data(self._data.position[:,6], self._data.position[:,7])

			#This is the new stuff, probably won't work yet.
			self.diode1_plot[0].set_data(self.retrieved_data[:,0], self.retrieved_data[:,1])
			self.diode2_plot[0].set_data(self.retrieved_data[:,2], self.retrieved_data[:,3])
			self.diode3_plot[0].set_data(self.retrieved_data[:,4], self.retrieved_data[:,5])
			self.diode4_plot[0].set_data(self.retrieved_data[:,6], self.retrieved_data[:,7])

			#Redisplay the plots		
			self.canvas.draw()
	


	def calculate_shift(self):
		'''Calculate how much the FEA has moved'''
		pass


	def update_grid(self,x,y,angle,color):
		'''Plot the pixel grid'''
				
		self.rotation_matrix = [[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]]

		self.xgrid_new = []
		self.ygrid_new = []

		#Reshape the position pairs to be a 2 column array
		original_pairs = np.transpose(np.vstack((self.xgrid,self.ygrid)))
		
		#Calculate the new pairs after applying the rotation matrix
		new_pairs = np.dot(original_pairs,self.rotation_matrix)

		#Break it back up into individual arrays for plotting
		self.xgrid_new = new_pairs[:,0] + x
		self.ygrid_new = new_pairs[:,1] + y
		
		if self.realtime_plot_checkbox.isChecked():
			
			#Assign the new data to the array for plotting
			self.pixel_plot_new[0].set_data(self.xgrid_new,self.ygrid_new)
			self.pixel_plot[0].set_data(self.xgrid,self.ygrid)
			
			#Plot the two grids
			self.canvas2.draw()
		
	def retrieve_queue(self):
 		read_counter = np.size(self._data.x1_position)
 		
 		#Update the amount of data plotted
 		self.new_data_size = self._buffer.qsize()
 		
		for looper in range(self.new_data_size):
			#print looper
			#timestart = time.time()
			newdata = self._buffer.get(True)
			#timeend = time.time()
			#print 'getting time ' + str(timeend-timestart)

			#This is what I originally had. However this got slow really fast. Fortunately it looks like the set_data plotting only needs the 
			#new data (as it overplots). So I don't need to make big arrays that slow everything down.
			#self.retrieved_data = np.vstack([self.retrieved_data,newdata])
			
			self.retrieved_data = newdata


		# print 'RETRIEVED DATA'
		# print self.retrieved_data
						



if __name__ == "__main__":
    #==========================================Setup Parameters
    
	try:
		_fromUtf8 = QtCore.QString.fromUtf8
	except AttributeError:
		_fromUtf8 = lambda s: s
	
	#Create the instances of the data and buffer classes
	buffer = Queue.Queue()
	
	#Create class instances
	data    = Position_data(buffer)
	#Make sure the thread dies when this thread is the only thing left
	#data.daemon = True
	
	app = QtGui.QApplication(sys.argv)
	display = Position_plots(data, buffer)
	sys.exit(app.exec_())
