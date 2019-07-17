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
	bkg_method <class 'str'> : default is "sigma"
	sub_method <class 'str'> : default is "median"
	sigma <class 'float'> : default is 5.0
	
Returns:
	n/a

Date: 27 Apr 2019
Last update: 16 Jul 2019
"""

__author__ = "Richard Camuccio"
__version__ = "1.2.0"

from astropy import units as u
from astropy.io import fits
from astropy.stats import SigmaClip
from astropy.stats import sigma_clipped_stats
from do_read import *
import astroscrappy
import configparser
import glob
import math
import numpy as np
import os
import time

def do_calibrate(object_list, master_dark, flatfield, output_dir, bkg_method="sigma", sub_method="median", sigma=5.0):
	"""Calibrate and save a series of raw object frames"""

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
		crmask, clean_data = astroscrappy.detect_cosmics(cal_data, inmask=None, satlevel=np.inf, sepmed=False, cleantype="medmask", fsmode="median")

		if bkg_method == "simple":

			if sub_method == "median":
				print(" [CAL][do_calibrate]: Calculating array median")
				median = np.median(clean_data)

				print(" [CAL][do_calibrate]: Subtracting median from array")
				bkgsub_data = clean_data - median

			elif sub_method == "mean":
				print(" [CAL][do_calibrate]: Calculating array mean")
				mean = np.mean(clean_data)

				print(" [CAL][do_calibrate]: Subtracting mean from array")
				bkgsub_data = clean_data - mean

			else:
				print(" [CAL][do_calibrate]: Calculating array median")
				median = np.median(clean_data)

				print(" [CAL][do_calibrate]: Subtracting median from array")
				bkgsub_data = clean_data - median

		elif bkg_method == "sigma":

			print(" [CAL][do_calibrate]: Calculating sigma-clipped statistics of array")
			mean, median, std = sigma_clipped_stats(clean_data, sigma=sigma)

			if sub_method == "median":
				print(" [CAL][do_calibrate]: Subtracting sigma-clipped median from array")
				bkgsub_data = clean_data - median

			elif sub_method == "mean":
				print(" [CAL][do_calibrate]: Subtracting sigma-clipped mean from array")
				bkgsub_data	= clean_data - mean

			else:
				print(" [CAL][do_calibrate]: Subtracting sigma-clipped median from array")
				bkgsub_data = clean_data - median

		elif bkg_method == "mask":

			print(" [CAL][do_calibrate]: Creating source mask for array")
			mask = make_source_mask(clean_data, snr=2, npixels=5, dilate_size=30)

			print(" [CAL][do_calibrate]: Calculating sigma-clipped statistics of array")
			mean, median, std = sigma_clipped_stats(clean_data, sigma=sigma, mask=mask)

			if sub_method == "median":
				print(" [CAL][do_calibrate]: Subtracting sigma-clipped median from array")
				bkgsub_data = clean_data - median

			elif sub_method == "mean":
				print(" [CAL][do_calibrate]: Subtracting sigma-clipped mean from array")
				bkgsub_data	= clean_data - mean

			else:
				print(" [CAL][do_calibrate]: Subtracting sigma-clipped median from array")
				bkgsub_data = clean_data - median

		else:

			print(" [CAL][do_calibrate]: Calculating sigma-clipped statistics of array")
			mean, median, std = sigma_clipped_stats(clean_data, sigma=sigma)

			if sub_method == "median":
				print(" [CAL][do_calibrate]: Subtracting sigma-clipped median from array")
				bkgsub_data = clean_data - median

			elif sub_method == "mean":
				print(" [CAL][do_calibrate]: Subtracting sigma-clipped mean from array")
				bkgsub_data	= clean_data - mean

			else:
				print(" [CAL][do_calibrate]: Subtracting sigma-clipped median from array")
				bkgsub_data = clean_data - median

		print()
		print(" [CAL][do_calibrate]: Running [do_read]")
		hdr = do_read(item, output_dir)
		print(" [CAL][do_calibrate]: Ending [do_read]")
		print()

		print(" [CAL][do_calibrate]: Converting reduced array to FITS")
		hdu = fits.PrimaryHDU(bkgsub_data, header=hdr)

		print(" [CAL][do_calibrate]: Writing reduced FITS to", output_dir)
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
	do_calibrate(object_list, master_dark, flatfield, output_dir)
	print(" [CAL]: Ending [do_calibrate]")
	print()

	# End script
	end = time.time()
	time = end - start
	print(" End of script.", "%.2f" % time, "seconds to complete.")