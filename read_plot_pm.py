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


class Diode():
	
	def __init__(self,x,y):
		'''Initialize the diode'''
		#Define the location of the diode based on the CAD model
		#X and Y are in the diode frame
		self.xcenter = x
		self.ycenter = y
		
		
		

class Position_data():
	

		
	def __init__(self):
		'''Initialize the data'''
		
		self.initialize_data()
		
		self.connected_to_usb = False

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
		self.zero_spot = np.zeros((1,8))

	def connect_to_usb(self):
		'''Connect to USB feed'''
	
		#list_of_usb_ports = serports.comports()
	
		#self.port = '/dev/tty.usbserial-FTT3QDXK'	#Small PCB Converter
		
		#self.port = '/dev/tty.usbserial-FTT31FFA'	#Bigger Converter
		#self.port = '/dev/tty.usbmodem411'
		self.baudrate = 115200
		self.parity = 'N'
		self.rtscts = False
		self.xonxoff = False
		#self.ser = serial.Serial(self.port, self.baudrate, parity=self.parity, rtscts=self.rtscts, xonxoff=self.xonxoff, timeout=1)
		try:
			self.ser = serial.Serial(self.port, self.baudrate)
			print 'Setting up USB connection:'
			print 'Port: ' + self.port
			print 'Baudrate: ' + str(self.baudrate)
			print 'Parity: ' + self.parity
			print 'RTSCTS: ' + str(self.rtscts)
			print 'XONXOFF: ' + str(self.xonxoff)    
			self.connected_to_usb = True
		except:
			print "Failed to make USB Connection"
        	





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
		
			   
			if self.connected_to_usb == False:
				self.connect_to_usb()
			
			
			
			if self.connected_to_usb == True:
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
		
	def zero_diodes(self):
    		pass
    	
    	
#     	if np.sum(self.position)==0:
#     		self.zero_spot = np.zeros((1,8))
#     	else:
#     		self.zero_spot = self.position[-1,:]	
#     	
	
	def save_data(self):
		'''Save the data'''
		
		#current_time = str(datetime.datetime.now())
		#Time since Jan 1, 1970 (verify with: time.gmtime(0))
		current_time = str(time.time())
		try:
			self.save_file.write(current_time + ', ')
			for k in range(8):
				self.save_file.write(str(self.position[-1,k]))
				if k < 7:
					self.save_file.write(', ')
			
			self.save_file.write('\n')
		except:
			print "Error in save loop - data probably not saved"
			



class Position_plots(QtGui.QMainWindow, FigureCanvas):

	def __init__(self, data):
		'''Initialize the GUI Window'''
		
		#Timing information
		self.ts_old = time.time()
		self.ts = time.time()
		
		#GUI stuff
		self.main_gui = QtGui.QMainWindow()
		self.setupUi(self.main_gui)
		
		#Plot stuff
		self.setup_diodes()
		self.setup_grid()
# 		self.x = []
# 		self.y = []

		#More GUI stuff
		self.record = False
		self.retranslateUi(self.main_gui)
		QtCore.QMetaObject.connectSlotsByName(self.main_gui)
		
		#Define the plot timer that updates the diodes / map
		self._timer = self.fig1.canvas.new_timer()
	        self._timer.interval = 110
        	self._timer.add_callback(self.update_display)
        	
        	#Give this class access to the serial data class
        	self._data = data
        	
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
        
        def start(self):
		if self.record == False:
			self.statusbar.showMessage("Monitoring Diodes")
		else:
			self.statusbar.showMessage("Monitoring Diodes - Recording data to: "+self.save_filename)

		self._timer.start()		

	def pause(self):
		self.statusbar.showMessage("Monitoring Paused")
		self._timer.stop()
		
	def record(self):
		if self.record == True:
			#Data is already recording, turn recording off

			#Stop recording
			self.record = False
			
			try:
				#Close the save file
				self._data.save_file.close()
				self.statusbar.showMessage("Data saved to file: " + self.save_filename)

			except:
				self.statusbar.showMessage("Error closing save file - data may be lost")
		else:
			#Start recording
			self.record = True
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
			
		
	def specify_filename(self):
		'''Determine the filename for the save file'''
		fname = QtGui.QFileDialog.getSaveFileName(caption="Select filename to record data to", directory="/Users/Oakley/Desktop/")

		#Add the .txt extension if it's not already there
		if fname[-4:] != ".txt":
			fname += ".txt"
			
		self.filename_box.setText(fname)
	
		#Advance the color wheel
		self._color_index += 1
		
		#Find the new zero point from the data class
		self._data.zero_diodes()

	def setupUi(self, MainWindow):
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
		self.verticalLayout.addWidget(self.livedata_button)
		self.existingdata_button = QtGui.QRadioButton(self.widget)
		self.existingdata_button.setObjectName(_fromUtf8("existingdata_button"))
		self.verticalLayout.addWidget(self.existingdata_button)
		self.fakedata_button = QtGui.QRadioButton(self.widget)
		self.fakedata_button.setChecked(True)
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
		self.play_button = QtGui.QToolButton(self.widget)
		self.play_button.setText(_fromUtf8(""))
		icon1 = QtGui.QIcon()
		icon1.addPixmap(QtGui.QPixmap(_fromUtf8("blue_play_button.jpeg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.play_button.setIcon(icon1)
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
		MainWindow.setCentralWidget(self.centralwidget)
		self.menubar = QtGui.QMenuBar(MainWindow)
		self.menubar.setGeometry(QtCore.QRect(0, 0, 998, 22))
		self.menubar.setObjectName(_fromUtf8("menubar"))
		MainWindow.setMenuBar(self.menubar)
		self.statusbar = QtGui.QStatusBar(MainWindow)
		self.statusbar.setObjectName(_fromUtf8("statusbar"))
		MainWindow.setStatusBar(self.statusbar)
		

		QtCore.QObject.connect(self.play_button, QtCore.SIGNAL(_fromUtf8("clicked()")), self.start)
		QtCore.QObject.connect(self.record_button, QtCore.SIGNAL(_fromUtf8("clicked()")), self.record)
		QtCore.QObject.connect(self.pause_button, QtCore.SIGNAL(_fromUtf8("clicked()")), self.pause)
		QtCore.QObject.connect(self.filename_button, QtCore.SIGNAL(_fromUtf8("clicked()")), self.specify_filename)

		
	def retranslateUi(self, MainWindow):
		MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
		self.datamode_label.setText(QtGui.QApplication.translate("MainWindow", "Data Mode", None, QtGui.QApplication.UnicodeUTF8))
		self.livedata_button.setText(QtGui.QApplication.translate("MainWindow", "Plot Live Data", None, QtGui.QApplication.UnicodeUTF8))
		self.existingdata_button.setText(QtGui.QApplication.translate("MainWindow", "Plot Existing Data", None, QtGui.QApplication.UnicodeUTF8))
		self.fakedata_button.setText(QtGui.QApplication.translate("MainWindow", "Plot Fake Data", None, QtGui.QApplication.UnicodeUTF8))
		self.recorddata_label.setText(QtGui.QApplication.translate("MainWindow", "Record Data", None, QtGui.QApplication.UnicodeUTF8))
		self.pause_button.setToolTip(QtGui.QApplication.translate("MainWindow", "Pause recording", None, QtGui.QApplication.UnicodeUTF8))
		self.record_button.setToolTip(QtGui.QApplication.translate("MainWindow", "Start / resume recording", None, QtGui.QApplication.UnicodeUTF8))
		self.filename_box.setText(QtGui.QApplication.translate("MainWindow", "/Users/Oakley/Desktop/deleteme.txt", None, QtGui.QApplication.UnicodeUTF8))
		self.filename_button.setText(QtGui.QApplication.translate("MainWindow", "Specify Filename", None, QtGui.QApplication.UnicodeUTF8))
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
		self.listWidget.item(counter-1).setSelected(True)
		#self.listWidget.setItemSelected(self.listWidget.item(counter-1), True)
		self.listWidget.setSortingEnabled(__sortingEnabled)

	def setup_grid(self):
		'''Set up the figure for plotting the pixel grid'''
		
		self.fig2 = Figure()
		self.fig2.set_size_inches(8,2.5)
		self.canvas2 = FigureCanvas(self.fig2)
		self.canvas2.setParent(self.pixel_plot_widget)
		self.pixel_map = self.fig2.add_subplot(111)
		
		self.pixel_plot_new = self.pixel_map.plot(0,0,color='r')
		self.pixel_plot = self.pixel_map.plot(0,0,color='k')
		
		self.initialize_grid_values()
		self.update_grid(0,0,0,'r')
		self.pixel_map.set_xlim([-10,10])
		self.pixel_map.set_ylim([-10,10])
		self.pixel_map.set_title('Pixel Map (APPROXIMATION ONLY!)')


	def initialize_grid_values(self):
		'''Initialize the pixel grid'''
		self.angle = 0		
		self.rotation_matrix = [[math.cos(self.angle),-math.sin(self.angle)],[math.sin(self.angle),math.cos(self.angle)]]

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
		self.xgrid_new = new_pairs[:,0]
		self.ygrid_new = new_pairs[:,1]
		
		#Assign the new data to the array for plotting
		self.pixel_plot_new[0].set_data(self.xgrid_new,self.ygrid_new)
		self.pixel_plot[0].set_data(self.xgrid,self.ygrid)
		
		#Plot the two grids
		self.canvas2.draw()
		

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
	
	def update_display(self):
		'''Update the plot windows'''
		
		#Update the diode plots
		self.update_diodes()
		
		#Calculate how much the pixel map has shifted
		self.calculate_shift()
		
		#Update the pixel grid display plot
		self.update_grid(random.uniform(-3,3),random.uniform(-3,3),random.uniform(-3,3),'k')
		
		#If set to record, start recording
		if self.record:
			self._data.save_data()

	def calculate_shift(self):
		pass
		
	def update_diodes(self):
		'''Update the diode maps'''
		self.ts = time.time()
		self.data_speed_label.setText(QtGui.QApplication.translate("MainWindow", "Data Rate = " + str(round(1. / (self.ts-self.ts_old),1)) + " Hz", None, QtGui.QApplication.UnicodeUTF8))
		self.ts_old = self.ts

		#x1 = newdata[0][:]
		#y1 = newdata[1][:]
		#print x1
		#print y1
		#self.line1.set_data(x1,y1)
		#self.x.append(newdata[0])
		#self.y.append(newdata[1])
		self._data.fake_data = self.fakedata_button.isChecked()
		
		#This is sort of weird way to find the selected port. Other methods seem to fail though
		#The port will be auto-selected, but doesn't react the same as user-selected.
		#Weird
		selected_ports = self.listWidget.selectedItems()
		self._data.port = selected_ports[0].text()

		self._data.read_cycle()
		data = self._data.position

		#Reposition the new data with respect to the zero point
		#plot_data = data - self._data.zero_spot
		#spot_color = self._color_wheel[self._color_index]
		#self.diode1_plot[0].set_color(spot_color)
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
	
	data    = Position_data()
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
