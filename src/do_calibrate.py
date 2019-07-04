# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CAL

The function [do_calibrate] dark reduces and flatfield corrects a series of object FITS frames

Args:
	object_list <class 'list'> : list of FITS file names (each name is <class 'str'>)
	master_dark <class 'astropy.nddata.ccddata.CCDData'> : a master dark FITS frames
	flatfield <class 'astropy.nddata.ccddata.CCDData'> : a normalized flatfield FITS frame
	output_dir <class 'str'> : path to directory for saving calibrated object frames
	
Returns:
	n/a

Date: 27 Apr 2019
Last update: 4 Jul 2019
"""

__author__ = "Richard Camuccio"
__version__ = "1.0"

from astropy import units as u
from astropy.io import fits
import ccdproc
import configparser
import glob
import numpy as np
import os
import time

def do_calibrate(object_list, master_dark, flatfield, output_dir):
	"""Calibrate a series of object frames with a master dark and flatfield"""

	for item in object_list:

		print(" [CAL]: Reading", item, "data ...")
		object_frame = ccdproc.fits_ccddata_reader(item, unit="adu")

		print(" [CAL]: Subtracting master dark from", item, "...")
		object_min_dark = ccdproc.subtract_dark(object_frame, master_dark, data_exposure=object_frame.header["exposure"]*u.second, dark_exposure=master_dark.header["exposure"]*u.second, scale=True)

		print(" [CAL]: Dividing", item, "by flatfield ...")
		cal_object_frame = ccdproc.flat_correct(object_min_dark, flatfield)

		print(" [CAL]: Saving frame", item, "to", output_dir, "...")
		ccdproc.fits_ccddata_writer(cal_object_frame, str(output_dir) + "/c-" + str(item))

	return

if __name__ == "__main__":

	print(" [CAL]: Running [do_calibrate] as script ...")
	start = time.time()

	print(" [CAL]: Reading configuration file ...")
	config = configparser.ConfigParser()
	config.read("/home/rcamuccio/Documents/CAL/config/config.ini")

	print(" [CAL]: Parsing directory paths ...")
	object_dir = config["do_calibrate"]["input_dir_obj"]
	dark_dir = config["do_calibrate"]["input_dir_dark"]
	flat_dir = config["do_calibrate"]["input_dir_flat"]
	output_dir = config["do_calibrate"]["output_dir"]

	print(" [CAL]: Checking if output path exists ...")
	if not os.path.exists(output_dir):
		print(" [CAL]: Creating output directory", output_dir, "...")
		os.makedirs(output_dir)

	print(" [CAL]: Reading master dark frame ...")
	master_dark = ccdproc.fits_ccddata_reader(dark_dir + "/master-dark.fit", unit="adu")

	print(" [CAL]: Reading flatfield frame ...")
	flatfield = ccdproc.fits_ccddata_reader(flat_dir + "/flatfield.fit", unit="adu")

	print(" [CAL]: Changing to", object_dir, "as current working directory ...")
	os.chdir(object_dir)

	object_list = []

	for frame in glob.glob("*.fit"):

		if os.path.isfile(str(output_dir) + "/c-" + str(frame)):
			print(" [CAL]: Calibrated frame of", frame, "already exists ...")
			print(" [CAL]: Skipping calibration on frame", frame, "...")

		else:
			print(" [CAL]: Adding", frame, "to calibration list ...")
			object_list.append(frame)

	print(" [CAL]: Running [do_calibrate] ...")
	do_calibrate(object_list, master_dark, flatfield, output_dir)

	end = time.time()
	time = end - start
	print()
	print(" [CAL]: Script [do_calibrate] completed in", "%.2f" % time, "s")