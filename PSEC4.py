import matplotlib.pyplot as plt
import bokeh.plotting as bkh
import os
import datetime
import subprocess

### FILEPATH TO PSEC4 CODE DIRECTORY!!! SET THIS!!!!!! ###
DIR = '/home/wizenedchimp/Documents/LAPPD-Project/run-psec4-master'


oname = raw_input('Please enter a filename (blank for automatic):')
if oname == '':
	t = datetime.datetime.now()
	oname = 'sample_'+str(t.year)+'-'+str(t.month)+'-'+str(t.day)+'_'+str(t.hour)+'h'+str(t.minute)+'m'
oname = DIR+'/DATA/'+oname

print 'Writing to %s.txt' % oname
N = raw_input('Please enter the number of samples you want to take: ')
N = int(N)

command = [DIR+'/bin/LogData', str(oname), str(N), '0']
print command
psec = subprocess.Popen(command)
psec.wait()


# Samples is a list, and each sample contains
#  a set of 6 lists which are the channels readings

samples = []
channels = [[],[],[],[],[],[],[]]
j = 0
with open(oname+'.txt', 'r') as f:
	for line in f:
		if line[0] == '#':
			continue
		else:
			line = line.split()
			for i in range(6):
				channels[i+1].append(line[i])
			channels[0].append(j)
			j += 1
		if j%256 == 0:
			samples.append(channels)
			channels = [[],[],[],[],[],[],[]]
print 'Read out %d samples, in %d lines' % (len(samples), j)

#recover the user inputted name so it can be applied to graphs and whatever
stamp = oname.split('/')[-1].strip('.txt')

# output graph to a static HTML file
bkh.output_file(stamp+'.html')

#create plot object
p = bkh.figure(plot_width=1000, title=stamp, x_axis_label='N', y_axis_label='Voltage, V')

# Read the channels from each sample into long lists for plotting
channels = [[],[],[],[],[],[]]
for sample in samples:
	for i in range(6):
		for data in sample[i]:
			channels[i].append(data)
j = range(len(channels[0]))

# Plot the data
col = ['red', 'blue', 'orange', 'green', 'purple', 'black']
i = 1
#add data to the plot object
for channel in channels:
	p.line(j, channel, legend='Channel '+str(i), line_width=1, line_color=col[i-1])
	i += 1

# set ranges
p.y_range = Range1d(1.1*vmin, 1.1*vmax)

bkh.save(p)