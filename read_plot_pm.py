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

#==========================================Setup Parameters
#live_data = 1 for live feed off the RS422 signal from the control box
#live_data = 0 for analyzing stored data
live_data = 1
skip = 1
filename='/Users/Oakley/Documents/Work/microx/position_monitor/testing/test_liveread.txt'

#==========================================Set up the Connection to USB
if live_data == 1:
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


#==========================================Read Existing data
if live_data == 0:
	filename = '/Users/Oakley/Documents/Work/microx/position_monitor/3-23-2012/pm1.txt'
	file_exist = os.path.exists(filename)
	
	#Exit program if given filename doesn't exists
	if file_exist == False:
		print 'Error - file: ' + filename
		print 'Does not exist'
		sys.exit()
	
	pm_data_file = open(filename,'r')
	print "Opening File: ", pm_data_file.name
	data_array = np.genfromtxt(pm_data_file,delimiter='\t',dtype='f')
	
	
	x1_norm 		= data_array[:,0]
	x1				= data_array[:,1]
	y1_norm 		= data_array[:,2]
	y1				= data_array[:,3]
	
	x2_norm 		= data_array[:,4]
	x2 				= data_array[:,5]
	y2_norm 		= data_array[:,6]
	y2 				= data_array[:,7]
	
	x3_norm 		= data_array[:,8]
	x3 				= data_array[:,9]
	y3_norm 		= data_array[:,10]
	y3 				= data_array[:,11]
	
	x4_norm 		= data_array[12,:]
	x4 				= data_array[13,:]
	y4_norm 		= data_array[14,:]
	y4 				= data_array[15,:]
	
	x1_position = x1 / x1_norm
	y1_position = y1 / y1_norm
	x2_position = x2 / x2_norm
	y2_position = y2 / y2_norm
	x3_position = x3 / x3_norm
	y3_position = y3 / y3_norm
	x4_position = x4 / x4_norm
	y4_position = y4 / y4_norm


#==========================================Read Live data
if live_data == 1:
	print 'Attempting to read live data'
	
	#==========================================Read the data
	#Read until the FS=1 (i.e. we're looking at diode #1)
	
	
	
	#Data is separated into 32 8-bit bytes. 2 bytes for each parameter (x,x_norm, etc.)
	#data = ser.read(size = 32)


	#==========================================Reorganize the data
	byte = []
	bitarray = []
	original_bitarray = []
	bit14array = []
	valuearray = []
	synced = 0
	sync_attempt = 0
	read_cycle = 1
	
	while synced == 0 and sync_attempt < 100:
		prefix = []
		sync_test_byte = ser.read()
		sync_test_int = ord(sync_test_byte)
		sync_test_bitarray = bin(sync_test_int)[2:]
		missing_length = 8 - len(sync_test_bitarray)
		for k in range(missing_length):
			sync_test_bitarray = '0' + sync_test_bitarray
				 
		print sync_test_bitarray
		if sync_test_bitarray[0] == '1':
			synced = 1
			byte.append(sync_test_byte)
		
		sync_attempt += 1
	
	for k in range(31):
		byte.append(ser.read())
	
	for read_cycle in range(1):
		if skip == 1:
			#Each diode sends 2 bytes worth of data structured as:
				#Frame-sync bit, B13 - B7
				#Frame-sync bit, B6  - B0
				#The data bits (B13 - B0) are arranged MSB - LSB
				 
			# return an integer representing the Unicode code point of the character
			for k in range(32):
				byte_to_int = ord(byte[k])
				
				original_bitarray.append(bin(byte_to_int)[3:])
				bitarray.append(original_bitarray[k])
				missing_length = 7 - len(bitarray[k])

				for addzeros in range(missing_length):
					bitarray[k] = '0' + bitarray[k]
				# now bitarray contains a string with 0s and 1s
			

				
			for k in range(16):
				#combine the two bitarrays
				#Put the bits back together and put it into a float variable for easy division
		
				bit14array.append(bitarray[2*k]+bitarray[2*k+1])
				valuearray.append(float(int(bit14array[k],2)))	

			
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
				if printinfo%2==0:
					print byte[printinfo], '  ', original_bitarray[printinfo],'   ', bitarray[printinfo], '   ', bit14array[printinfo/2], '   ',valuearray[printinfo/2]

				if printinfo%2==1:
					print byte[printinfo], '  ',  original_bitarray[printinfo],'   ', bitarray[printinfo]


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
				
	#==========================================Save the data
	current_time = str(datetime.datetime.now())
	
	#print "Saved Data: ", data_tosave_filename
	



#==========================================Calculate the Shift
#Here's where the magic will happen



#==========================================Plot the Diode Spots
#plt.ion()
if live_data == 0:
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



