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

import random

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib.lines import Line2D


import serial
import serial.tools.list_ports as serports
#import struct
import math
import os.path
import sys
import datetime
import time

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
		self.position = []
		

	def connect_to_usb(self):
		'''Connect to USB feed'''
	
		list_of_usb_ports = serports.comports()
		print 'Possible USB ports = '
		print list_of_usb_ports
		#Replace above with command line or GUI option menu
		
		self.port = '/dev/tty.usbserial-FTT3QDXK'
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
		self.x1_position.extend(self.valuearray[1] / self.valuearray[0])
		self.y1_position.extend(self.valuearray[3] / self.valuearray[2])
		self.x2_position = self.valuearray[5] / self.valuearray[4]
		self.y2_position = self.valuearray[7] / self.valuearray[6]
		self.x3_position = self.valuearray[9] / self.valuearray[8]
		self.y3_position = self.valuearray[11] / self.valuearray[10]
		self.x4_position = self.valuearray[13] / self.valuearray[12]
		self.y4_position = self.valuearray[15] / self.valuearray[14]
			
		self.position = [self.x1_position,self.y1_position]#,self.x2_position,self.y2_position,self.x3_position,self.y3_position,self.x4_position,self.y4_position]
	
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
		'''Search for the frame sync byte'''
		while sync_attempt < 100:
		
			#Read in a byte (will be an ascii character)
			sync_test_byte = self.ser.read(1)

			#Convert byte to integer (needed to perform operations on)
			sync_test_int = ord(sync_test_byte)
			print sync_test_int
			
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
		print time.time()
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
		
			#self.print_positions()
		else:
			r = random.uniform(-3,3)
			self.x1_position.append(r)
			self.y1_position.append(r)
			self.position = np.ones(8)*r
		
		yield self.position
		#yield [self.x1_position, self.y1_position]
	
	def read_31_bytes(self):
		'''Read the next 31 bytes'''
		print 'Attempting to read live data'
		self.cycle_bit15array = []
		self.cycle_valuearray = []
		
		for k in range(1,32):
			self.cycle_byte.append(self.ser.read(1))
			
			# return an integer representing the Unicode code point of the character
			self.cycle_byte_to_int.append(ord(self.cycle_byte[k]))
			print ord(self.cycle_byte[k])
		
			if (k % 2 == 1):
			
				#Each diode sends 2 bytes worth of data structured as:
				#Frame-sync bit, B13 - B7
				#Frame-sync bit, B6  - B0
				#The data bits (B13 - B0) are arranged MSB - LSB
	
				#Zero the frame sync
				desynced1 = self.cycle_byte_to_int[k-1] & ~(1 << 7)
				desynced2 = self.cycle_byte_to_int[k]   & ~(1 << 7)
			
				#combine the two bitarrays
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
		#current_time = str(datetime.datetime.now())

		#print "Saved Data: ", data_tosave_filename




class Position_plots():
	
	def __init__(self):
		'''Initialize Class'''
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
		self.line1 = Line2D([],[],color='r*')
		
		self.diode1 = self.fig1.add_subplot(2,2,1)
		#self.diode1.plot([],[],'k.')
		self.diode1.set_xlabel('X Position [mm]')
		self.diode1.set_ylabel('X Position [mm]')
		self.diode1.set_title('Diode 1')
		
		# self.diode2 = self.fig1.add_subplot(2,2,2)
# 		self.diode2.plot([],[],'k.')
# 		self.diode2.set_xlabel('X Position [mm]')
# 		self.diode2.set_ylabel('X Position [mm]')
# 		self.diode2.set_title('Diode 2')
# 		
# 		self.diode3 = self.fig1.add_subplot(2,2,3)
# 		self.diode3.plot([],[],'k.')
# 		self.diode3.set_xlabel('X Position [mm]')
# 		self.diode3.set_ylabel('X Position [mm]')
# 		self.diode3.set_title('Diode 3')		
# 		
# 		self.diode4 = self.fig1.add_subplot(2,2,4)
# 		self.diode4.plot([],[],'k.')
# 		self.diode4.set_xlabel('X Position [mm]')
# 		self.diode4.set_ylabel('X Position [mm]')
# 		self.diode4.set_title('Diode 4')
# 				
		datasize=0		
		if (datasize==0):
			self.diode1.set_xlim([-5,5])
			self.diode1.set_ylim([-5,5])
			# self.diode2.set_xlim([-5,5])
# 			self.diode2.set_ylim([-5,5])
# 			self.diode3.set_xlim([-5,5])
# 			self.diode3.set_ylim([-5,5])
# 			self.diode4.set_xlim([-5,5])
# 			self.diode4.set_ylim([-5,5])		

		#self.fig1.show()
		self.diode1.figure.canvas.draw()
	
	def update_display(self,newdata):
		'''Update the plot windows'''
		#self.update_grid(data)
		#print newdata
		self.update_diodes(newdata)
		#return a
		
	def update_grid(self, data):
		'''Update the pixel grid'''

	
	def update_diodes(self, newdata):
		'''Update the diode maps'''
		#x1 = newdata[0][:]
		#y1 = newdata[1][:]
		#print x1
		#print y1
		#self.line1.set_data(x1,y1)
		self.diode1.plot(newdata[0],newdata[1],'k.')
		#self.diode2.plot(newdata[2],newdata[3],'k.')
		#self.diode3.plot(newdata[4],newdata[5],'k.')
		#self.diode4.plot(newdata[6],newdata[7],'k.')
		#self.diode1.figure.canvas.draw()

		#return self.line1

	

if __name__ == "__main__":
	#==========================================Setup Parameters
	
	#Create class instances
	data    = Position_data(fake_data=True)
	display = Position_plots()
	
	sync_attempt = 0
	read_cycle = 1

	#Using the Position Plots Class fig1, get data from the Position Data class (read_cycle function)
	#and display it using the Position Plots class (update_display function)
	#Do this every 2 milliseconds
	ani = animation.FuncAnimation(display.fig1, display.update_display, data.read_cycle, interval=1, blit=False)

	

	#Animation doesn't happen without this
	plt.show()

	#ser.close()
