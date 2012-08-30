#Data Format

#Inputs
#	live_data: Set to 1 for reading data off the control box in real time. Set to 0 for reading a previously recorded filename
#	Filename: filename to read if live_data = 0, filename to save if live_data = 1

#Outputs
#	None

#Save files
#	Saves the data in a csv file (using the filename input) if reading data live_data
#	Saves the figure plots (2 of them) regardless of live_data.
#	Note - program will not overwrite existing files

#Things to fix
#	Better interactivity with selecting a USB port
#	Right now the program parses everything into separate variables (x1,y1,x2,y2, etc.) for ease of understand. This is likely inefficient and should be changed later
#	Need the magic code for coordinate transformation
#	Is sys.exit() the proper way to exit a program?	

#==========================================Import necessary libraries
#import matplotlib.pyplot as plt

import numpy as np
#from time import sleep

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

import serial
import serial.tools.list_ports as serports
#import struct
import math
import os.path
import sys
import datetime
import time

class Position_data():

	def __init__(self):
		
		self.initialize_data()
			
		

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


	def calculate_positions(self):
		print self.valuearray
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
	
	
	def convert_from_twos_complement(self,value):
		'''Convert from twos complement'''
		#Check whether the input is positive (0 first bit) or negative (1 first bit)
		if value > 127:
	
			#Zero the sign bit
			value ^= (1<<7)
			
			#Add 1
			value += 1
			
			#Make negative
			value = -value
			
		return value
		
		
		
	def sync_feed(self,sync_attempt):
		while sync_attempt < 100:
		
			#Read in a byte (will be an ascii character)
			sync_test_byte = ser.read()
			
			#Convert byte to integer (needed to perform operations on)
			sync_test_int = ord(sync_test_byte)
			
			#Check to see if the first bit is a 1
			#This happens when the overall integer value is >= 128
			
			if sync_test_int >= 128:
				print 'Sync in: ' + str(sync_attempt) + ' attempts'
				return sync_test_byte
		
			sync_attempt += 1
			
		print 'Failed to sync in: ' + str(sync_attempt) + ' attempts'
		return 0;

	
	def read_cycle(self, ser):
		print 'Attempting to read live data'
		for k in range(1,32):
			self.byte.append(ser.read())
			
			# return an integer representing the Unicode code point of the character
			self.byte_to_int.append(ord(self.byte[k]))
		
			if (k % 2 == 1):
			
				#Each diode sends 2 bytes worth of data structured as:
				#Frame-sync bit, B13 - B7
				#Frame-sync bit, B6  - B0
				#The data bits (B13 - B0) are arranged MSB - LSB
	
				#Zero the frame sync
				desynced1 = self.byte_to_int[k-1] & ~(1 << 7)
				desynced2 = self.byte_to_int[k]   & ~(1 << 7)
			
				#combine the two bitarrays
				self.bit15array.append(desynced1 | (desynced2 << 7))
							
				#Put the bits back together and put it into a float variable for easy division
				self.valuearray.append(float(self.convert_from_twos_complement(self.bit15array[(k-1)/2])))
				

		
	def print_positions(self):
		print 'Byte original bitarray bitarray bit14array valuearray'
		for printinfo in range(32):
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
		current_time = str(datetime.datetime.now())

		#print "Saved Data: ", data_tosave_filename




class Position_plots():
	
	def __init__(self):
		#self.setup_grid()
		self.setup_diodes()
		

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
		self.fig1 = plt.figure()
		
		self.diode1 = self.fig1.add_subplot(2,2,1)
		self.diode1.plot([],[],'k.')
		self.diode1.set_xlabel('X Position [mm]')
		self.diode1.set_ylabel('X Position [mm]')
		self.diode1.set_title('Diode 1')
		
		self.diode2 = self.fig1.add_subplot(2,2,2)
		self.diode2.plot([],[],'k.')
		self.diode2.set_xlabel('X Position [mm]')
		self.diode2.set_ylabel('X Position [mm]')
		self.diode2.set_title('Diode 2')
		
		self.diode3 = self.fig1.add_subplot(2,2,3)
		self.diode3.plot([],[],'k.')
		self.diode3.set_xlabel('X Position [mm]')
		self.diode3.set_ylabel('X Position [mm]')
		self.diode3.set_title('Diode 3')		
		
		self.diode4 = self.fig1.add_subplot(2,2,4)
		self.diode4.plot([],[],'k.')
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
		
	
	def update_display(self, data):
		'''Update the plot windows'''
		self.update_grid(data)
		self.update_diodes(data)
		
	def update_grid(self, data):
		'''Update the pixel grid'''

	
	def update_diodes(self, data):
		'''Update the diode maps'''





if __name__ == "__main__":
	#==========================================Setup Parameters
	#live_data = 1 for live feed off the RS422 signal from the control box
	#live_data = 0 for analyzing stored data
	live_data = 1
	skip = 1
	filename='/Users/Oakley/Documents/Work/microx/position_monitor/testing/test_liveread.txt'
	
	#==========================================Set up the Connection to USB
	list_of_usb_ports = serports.comports()
	print 'Possible USB ports = '
	print list_of_usb_ports
	#Replace above with command line or GUI option menu
	
	port = '/dev/tty.usbserial-FTT3QDXK'
	baudrate = 115200
	parity = 'N'
	rtscts = False
	xonxoff = False
	ser = serial.Serial(port, baudrate, parity=parity, rtscts=rtscts, xonxoff=xonxoff, timeout=1)
	
	print 'Setting up USB connection:'
	print 'Port: ' + port
	print 'Baudrate: ' + str(baudrate)
	print 'Parity: ' + parity
	print 'RTSCTS: ' + str(rtscts)
	print 'XONXOFF: ' + str(xonxoff)
	
	data    = Position_data()
	display = Position_plots()
	
	sync_attempt = 0
	read_cycle = 1
	
	for read_cycle in range(1):
		
		data.byte.append(data.sync_feed(sync_attempt))
		data.byte_to_int.append(ord(data.byte[0]))
		
		if data.byte_to_int[0] < 128:
			print "Failed to Sync. Exiting"
			#return 0;
			sys.exit()
		
		data.read_cycle(ser)
	
		data.calculate_positions()
	
		data.print_positions()
	
		#display.update_display(data)
	
		print "sleeping"
		#time.sleep(1)
		print "waking"
		print read_cycle
	ser.close()
	
	#plt.show()
		