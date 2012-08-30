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

#==========================================Plot Initial Pixel Grid

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
filename = '/Users/Oakley/Documents/Work/microx/position_monitor/3-23-2012/pm1.txt'
filename = '/Users/Oakley/Documents/Work/microx/position_monitor/wallops/pm-random-thrust-warm.txt'
file_exist = os.path.exists(filename)

#Exit program if given filename doesn't exists
if file_exist == False:
	print 'Error - file: ' + filename
	print 'Does not exist'
	sys.exit()

pm_data_file = open(filename,'r')
print "Opening File: ", pm_data_file.name
data_array = np.genfromtxt(pm_data_file,delimiter='\t',dtype='f')


x1_norm = data_array[:,0]
x1	= data_array[:,1]
y1_norm	= data_array[:,2]
y1	= data_array[:,3]

x2_norm = data_array[:,4]
x2 	= data_array[:,5]
y2_norm = data_array[:,6]
y2 	= data_array[:,7]

x3_norm = data_array[:,8]
x3 	= data_array[:,9]
y3_norm = data_array[:,10]
y3 	= data_array[:,11]

x4_norm = data_array[:,12]
x4 	= data_array[:,13]
y4_norm = data_array[:,14]
y4 	= data_array[:,15]

x1_position = x1 / x1_norm
y1_position = y1 / y1_norm
x2_position = x2 / x2_norm
y2_position = y2 / y2_norm
x3_position = x3 / x3_norm
y3_position = y3 / y3_norm
x4_position = x4 / x4_norm
y4_position = y4 / y4_norm

print 'Data length is: ' + str(np.size(x1_position)) + ' samples'


#==========================================Plot the Diode Spots
#plt.ion()
fig2 = plt.figure()
diode_fig = fig2.add_subplot(111)


for k in range(np.size(x1_position)):
	diode1 = plt.subplot(2,2,1)
	plt.plot(x1_position[k],y1_position[k],'.k')
	plt.xlabel('X Position [mm]')
	plt.ylabel('X Position [mm]')
	plt.title('Diode 1')
	
	diode2 = plt.subplot(2,2,2)
	plt.plot(x2_position[k],y2_position[k],'.k')
	plt.xlabel('X Position [mm]')
	plt.ylabel('X Position [mm]')
	plt.title('Diode 2')
	
	diode3 = plt.subplot(2,2,3)
	plt.plot(x3_position[k],y3_position[k],'.k')
	plt.xlabel('X Position [mm]')
	plt.ylabel('X Position [mm]')
	plt.title('Diode 3')
	
	diode4 = plt.subplot(2,2,4)
	plt.plot(x4_position[k],y4_position[k],'.k')
	plt.xlabel('X Position [mm]')
	plt.ylabel('X Position [mm]')
	plt.title('Diode 4')
	
	if (k==0):
		diode1.set_xlim([-5,5])
		diode1.set_ylim([-5,5])
		diode2.set_xlim([-5,5])
		diode2.set_ylim([-5,5])
		diode3.set_xlim([-5,5])
		diode3.set_ylim([-5,5])
		diode4.set_xlim([-5,5])
		diode4.set_ylim([-5,5])

	
	#fig2.savefig('/Users/Oakley/Documents/Work/microx/position_monitor/3-23-2012/movie_figures/'+str(k)+'.png',format='png')
	


#make_movie_images(filename)




#==========================================Determine the filename to save to
filename_base = filename[:-4]
diode_filename = filename_base + '_diode_figure.pdf'
detector_filename = filename_base + '_detector_figure.pdf'

print "Saving Figure: ", diode_filename
print "Saving Figure: ", detector_filename

fig2.savefig(diode_filename,format='pdf')


plt.show()