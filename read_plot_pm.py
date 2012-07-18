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
import matplotlib.pyplot as plt
import numpy as np
#from time import sleep
import serial
import serial.tools.list_ports as serports
#import struct
import math
import os.path
import sys
import datetime


#==========================================Define Grid Plotting Function
def plotgrid(xcenter,ycenter,angle,color,figure):
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



#==========================================Define Algorithm to convert from two's complement
def convert_from_twos_complement(value):

	#Check whether the input is positive (0 first bit) or negative (1 first bit)
	if value > 127:

		#Zero the sign bit
		value ^= (1<<7)
		
		#Add 1
		value += 1
		
		#Make negative
		value = -value
		
	return value
		
		
		
#==========================================Define Function to sync the RS422 feed		
def sync_feed(sync_attempt):
	while sync_attempt < 100:
	
		#Read in a byte (will be an ascii character)
		sync_test_byte = ser.read()
		
		#Convert byte to integer (needed to perform operations on)
		sync_test_int = ord(sync_test_byte)
		
		#Check to see if the first bit is a 1
		#This happens when the overall integer value is =>128
		
		if sync_test_int >= 128:
			print 'Sync in: ' + str(sync_attempt) + ' attempts'
			return sync_test_byte
	
		sync_attempt += 1
		
	print 'Failed to sync in: ' + str(sync_attempt) + ' attempts'
	return 0;




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





#==========================================Plot Initial Pixel Grid

if skip == 0:
	fig1 = plt.figure()
	detector_fig = fig1.add_subplot(111)
	plotgrid(0,0,0,'k',detector_fig)



#==========================================Obtain data

#===================Initial setup
data = []

x1 = []
x1_norm = []
y1 = []
y1_norm = []

x2 = []
x2_norm = []
y2 = []
y2_norm = []

x3 = []
x3_norm = []
y3 = []
y3_norm = []

x4 = []
x4_norm = []
y4 = []
y4_norm = []




#==========================================Read Live data

print 'Attempting to read live data'

#==========================================Read the data
#Read until the FS=1 (i.e. we're looking at diode #1)



#Data is separated into 32 8-bit bytes. 2 bytes for each parameter (x,x_norm, etc.)
#data = ser.read(size = 32)


#==========================================Reorganize the data
byte = []
byte_to_int = []
bit15array = []
valuearray = []
sync_attempt = 0
read_cycle = 1


for read_cycle in range(100):
	
	byte.append(sync_feed(sync_attempt))
	byte_to_int.append(ord(byte[0]))
	
	if byte_to_int[0] < 128:
		print "Failed to Sync. Exiting"
		#return 0;
		sys.exit()
	
	for k in range(1,32):
		byte.append(ser.read())
		
		# return an integer representing the Unicode code point of the character
		byte_to_int.append(ord(byte[k]))
	
		if (k % 2 == 1):
		
			#Each diode sends 2 bytes worth of data structured as:
			#Frame-sync bit, B13 - B7
			#Frame-sync bit, B6  - B0
			#The data bits (B13 - B0) are arranged MSB - LSB

			#Zero the frame sync
			desynced1 = byte_to_int[k-1] & ~(1 << 7)
			desynced2 = byte_to_int[k]   & ~(1 << 7)
		
			#combine the two bitarrays
			bit15array.append(desynced1 | (desynced2 << 7))
						
			#Put the bits back together and put it into a float variable for easy division
			valuearray.append(float(convert_from_twos_complement(bit15array[(k-1)/2])))
			

		
	#Calculate spot positions
	x1_position = valuearray[1] / valuearray[0]
	y1_position = valuearray[3] / valuearray[2]
	x2_position = valuearray[5] / valuearray[4]
	y2_position = valuearray[7] / valuearray[6]
	x3_position = valuearray[9] / valuearray[8]
	y3_position = valuearray[11] / valuearray[10]
	x4_position = valuearray[13] / valuearray[12]
	y4_position = valuearray[15] / valuearray[14]



	print 'Byte original bitarray bitarray bit14array valuearray'
	for printinfo in range(32):
		if printinfo % 2==0:
			print byte[printinfo], '  ', byte_to_int[printinfo]

		if printinfo % 2==1:
			print byte[printinfo],'   ', byte_to_int[printinfo],'   ', bit15array[(printinfo-1)/2], '   ',valuearray[(printinfo-1)/2]


	print
	print 'Positions'
	print x1_position
	print y1_position
	print x2_position
	print y2_position
	print x3_position
	print y3_position
	print x4_position
	print y4_position					





	#==========================================Plot the Diode Spots
	plt.ion()
	fig2 = plt.figure()
	diode_fig = fig2.add_subplot(111)
	
	diode1 = plt.subplot(2,2,1)
	plt.plot(x1_position,y1_position,'k.')
	plt.xlabel('X Position [mm]')
	plt.ylabel('X Position [mm]')
	plt.title('Diode 1')
	
	diode2 = plt.subplot(2,2,2)
	plt.plot(x2_position,y2_position,'k.')
	plt.xlabel('X Position [mm]')
	plt.ylabel('X Position [mm]')
	plt.title('Diode 2')
	
	diode3 = plt.subplot(2,2,3)
	plt.plot(x3_position,y3_position,'k.')
	plt.xlabel('X Position [mm]')
	plt.ylabel('X Position [mm]')
	plt.title('Diode 3')
	
	diode4 = plt.subplot(2,2,4)
	plt.plot(x4_position,y4_position,'k.')
	plt.xlabel('X Position [mm]')
	plt.ylabel('X Position [mm]')
	plt.title('Diode 4')
	
	diode1.set_xlim([-5,5])
	diode1.set_ylim([-5,5])
	diode2.set_xlim([-5,5])
	diode2.set_ylim([-5,5])
	diode3.set_xlim([-5,5])
	diode3.set_ylim([-5,5])
	diode4.set_xlim([-5,5])
	diode4.set_ylim([-5,5])

	#plt.show()

#==========================================Save the data
current_time = str(datetime.datetime.now())

#print "Saved Data: ", data_tosave_filename




#==========================================Calculate the Shift
#Here's where the magic will happen

#==========================================Plot the Current Pixel Grid
if skip == 0:
	plotgrid(1,1,15/57.3,'r',detector_fig)

#==========================================Save the plot
# filename_base = filename[:-4]
# diode_filename = filename_base + '_diode_figure.pdf'
# detector_filename = filename_base + '_detector_figure.pdf'
# print "Saving Figure: ", diode_filename
# print "Saving Figure: ", detector_filename
# 
# fig1.savefig(detector_filename,format='pdf')
# fig2.savefig(diode_filename,format='pdf')
# plt.show()


# command = ('mencoder',
#            'mf://*.png',
#            '-mf',
#            'type=png:w=800:h=600:fps=25',
#            '-ovc',
#            'lavc',
#            '-lavcopts',
#            'vcodec=mpeg4',
#            '-oac',
#            'copy',
#            '-o',
#            'output.avi')
# 
# os.spawnvp(os.P_WAIT, 'mencoder', command)
#

ser.close()


	