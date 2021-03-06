#!/usr/bin/env python
# Fit a double gaussian to a PSEC logfile, and by knowing the velocity calculate the position.

import matplotlib.pyplot as plt
import read_PSEC as psec

import numpy as np
import os
from Tkinter import *
import tkFileDialog
import tkMessageBox
import bokeh.plotting as bkh
from scipy import optimize
from bokeh.models import Span

# Toggle plotting
plot = 0

def chisquare(fobs, fgen):
    chi = 0.0
    k = 0.
    for obs, gen in zip(fobs, fgen):
        if obs == 0 or gen == 0:
            continue
        chi += (float(obs)-float(gen))**2/float(abs(obs))
        k += 1.
    return chi/k

def gaussian(x, height, center, width):
    return height*np.exp(-(x - center)**2/(2*width**2))

def two_gaussians(x, h1, c1, w1, h2, c2, w2, offset=0):
    return (gaussian(x, h1, c1, w1) +
        gaussian(x, h2, c2, w2) + offset)

cwd = os.getcwd()
# Get the data file from a dialogue box and open it. Also store the filename.
root = Tk()
root.withdraw()
root.update()
f = tkFileDialog.askopenfile(mode='rb', 
    initialfile=cwd, 
    title='Select a file', 
    filetypes = (("TXT Files", "*.txt"),("all files","*.*")))
root.destroy()
try:
    fname = f.name
except:
    print("No file selected")
    exit()
f.close()

# Get the data
big_ts, samples = psec.read(fname)

#Make a maller version of ts to use for individual samples
ts = np.arange(0.0, 25.6, 0.1)

ch = raw_input("What channel on the PSEC? (1-6): ")
ch = int(ch)-1
# position = float(raw_input("What position on the tile are we at (cm): "))/100
electronVelocity = 1.2e8

positions = []

if plot:
    # -- Boleh Fiddling -- #
    # Set up write file
    oname = fname.replace('.txt', '.html')
    ofile = bkh.output_file(fname.replace('.txt', '.html'), title=fname)

    # Create figure
    title = fname.split('/')[-1][:-5]
    # Data
    p   = bkh.figure(plot_width=1000, title=title+' Signal', 
        x_axis_label='t-t0, ns', y_axis_label='Voltage, mV', )

    big_volts = []
    all_gaussians = []
    all_guesses = []

superluminal = 0

for key, sample in samples.iteritems():
    ## Fit a double gaussian to the data ##
    # Get channel data
    volts = sample[ch,:]

    # Chisq error function
    errfunc = lambda p, x, y: (two_gaussians(x, *p) - y)**2

    # Guess the locations of the gaussians
    halfmax_volt = 0.5 * np.amin(volts)
    halfmax_t1 = np.argmax(volts<halfmax_volt)
    halfmax_t1 = ts[halfmax_t1]

    halfmax_t2 = np.argmax(volts[::-1] < halfmax_volt)
    halfmax_t2 = ts[-1*halfmax_t2]

           #   h1,   c1,   w1]
    guess = [halfmax_volt, halfmax_t1, 0.1,
            halfmax_volt, halfmax_t2, 0.1,
            np.mean(sample[2,:]) ] # y offset

    # Optimise gaussian fit
    optim, success = optimize.leastsq(errfunc, guess[:], args=(ts, volts))

    chisq = chisquare(volts, two_gaussians(ts, *optim))

    # Get the time differences
    time_difference = abs(optim[4]-optim[1])*1e-9 # Convert to ns

    # Calculate the position
    position = 0.06 - (.5*time_difference * electronVelocity)

    if position > 0.0 and position < 0.058:
        positions.append(position*100)
    elif position < 0.0:
        superluminal += 1
    #     print("Time delay = %.4g" % time_difference)
    #     fig, ax = plt.subplots(figsize=[10,6])
    #     ax.plot(ts, volts, color='black', label='Raw Data')
    #     ax.plot(ts, two_gaussians(ts, *optim), color='red', label='Double Gaussian Fit')
    #     ax.set_xlabel('Time, ns')
    #     ax.set_ylabel('Voltage, mV')
    #     ax.legend()
    #     plt.tight_layout()
    #     plt.show()
    # positions.append(position*100)

print("I recorded %d superluminal velocities, of %d samples." % 
    (superluminal, len(positions)))
print(np.mean(np.array(positions)))
print(np.std(np.array(positions)))

plt.hist(positions, facecolor='green', edgecolor='black', bins=30, range=[0, 6])
plt.title("Positions of signals")
plt.ylabel('Frequency')
plt.xlabel('Position, cm')
plt.show()