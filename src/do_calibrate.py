# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CAL

The function [do_calibrate] calibrates a series of object FITS frames: dark reduction,
	flatfield correction, and cosmic ray annihilation

Args:
	object_list <class 'list'> : list of FITS file names (each name is <class 'str'>)
	master_dark  <class 'numpy.ndarray'> : a master dark data array
	flatfield  <class 'numpy.ndarray'> : a normalized flatfield data array
	output_dir <class 'str'> : path to directory for saving calibrated object frames
	
Returns:
	n/a

Date: 27 Apr 2019
Last update: 6 Jul 2019
"""

__author__ = "Richard Camuccio"
__version__ = "1.1.0"

from astropy import units as u
from astropy.io import fits
from do_read import *
import astroscrappy
import configparser
import glob
import math
import numpy as np
import os
import time

def do_calibrate(object_list, master_dark, flatfield, output_dir):
	"""Calibrate a series of object frames"""

	for item in object_list:

		print(" [CAL][do_calibrate]: Opening frame", item)
		raw_fits = fits.open(item)

		print(" [CAL][do_calibrate]: Reading FITS data")
		raw_data = raw_fits[0].data

		print(" [CAL][do_calibrate]: Subtracting master dark")
		object_min_dark = raw_data - master_dark

		print(" [CAL][do_calibrate]: Dividing flatfield")
		cal_data = object_min_dark / flatfield

		print(" [CAL][do_calibrate]: Detecting and removing cosmic rays")
		crmask, clean_data = astroscrappy.detect_cosmics(cal_data, inmask=None, sigclip=4.0, satlevel=np.inf, sepmed=False, cleantype="medmask", fsmode="median")

		print(" [CAL][do_calibrate]: Running [do_read]")
		hdr = do_read(item, output_dir)
		print(" [CAL][do_calibrate]: Ending [do_read]")

		print(" [CAL][do_calibrate]: Converting cleaned array to FITS")
		hdu = fits.PrimaryHDU(clean_data, header=hdr)

		print(" [CAL][do_calibrate]: Writing cleaned FITS to", output_dir)
		hdu.writeto(output_dir + "/c-" + str(item))

	return

if __name__ == "__main__":

	# Begin script
	os.system("clear")
	print(" Running CAL")
	print()
	print(" [CAL]: Running [do_calibrate] as script")
	start = time.time()

	# Read configuration file
	print(" [CAL]: Reading configuration file")
	config = configparser.ConfigParser()
	config.read("/home/rcamuccio/Documents/CAL/config/config.ini")

	# Assign paths to variables
	print(" [CAL]: Parsing directory paths")
	object_dir = config["do_calibrate"]["input_dir_obj"]
	dark_dir = config["do_calibrate"]["input_dir_dark"]
	flat_dir = config["do_calibrate"]["input_dir_flat"]
	output_dir = config["do_calibrate"]["output_dir"]

	# Check if output path needs to be created
	print(" [CAL]: Checking if output path exists")
	if not os.path.exists(output_dir):
		print(" [CAL]: Creating output directory", output_dir)
		os.makedirs(output_dir)

	# Open and read master dark
	print(" [CAL]: Reading master dark frame")
	master_dark_fits = fits.open(dark_dir + "/master-dark.fit")
	master_dark = master_dark_fits[0].data

	# Open and read flatfield
	print(" [CAL]: Reading flatfield frame")
	flatfield_fits = fits.open(flat_dir + "/flatfield.fit")
	flatfield = flatfield_fits[0].data

	# Change to object directory
	print(" [CAL]: Changing to", object_dir, "as current working directory")
	os.chdir(object_dir)

	# Populate object list
	object_list = []

	for frame in glob.glob("*.fit"):

		if os.path.isfile(str(output_dir) + "/c-" + str(frame)):
			print(" [CAL]: Calibrated frame of", frame, "already exists")
			print(" [CAL]: Skipping calibration on frame", frame)

		else:
			print(" [CAL]: Adding", frame, "to calibration list")
			object_list.append(frame)

	print(" [CAL]: Sorting object list")
	object_list = sorted(object_list)

	# Run function
	print()
	print(" [CAL]: Running [do_calibrate]")
	print()
	do_calibrate(object_list, master_dark, flatfield, output_dir)
	print()
	print(" [CAL]: Ending [do_calibrate]")
	print()

	# End script
	end = time.time()
	time = end - start
	print(" End of script.", "%.2f" % time, "seconds to complete.")