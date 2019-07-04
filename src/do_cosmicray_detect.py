# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CAL

The function [do_cosmicray_detect] detects and removes cosmic ray signals from a series of FITS frames

Args:
	object_list <class 'list'> : list of FITS file names (each name is <class 'str'>)
	output_dir <class 'str'> : path to directory for saving cleaned object frames

Returns:
	n/a

Date: 3 Jun 2019
Last update: 4 Jul 2019
"""

__author__ = "Richard Camuccio"
__version__ = "1.0"

from astropy import units as u
from astropy.io import fits
import astroscrappy
import configparser
import glob
import numpy as np
import os
import time

def do_cosmicray_detect(object_list, output_dir):
	"""Detect and remove cosmic rays from a series of FITS frames"""

	for item in object_list:

		print(" [CAL]: Opening frame", item, "...")
		frame = fits.open(item)

		print(" [CAL]: Reading frame", item, "data ...")
		frame_data = frame[0].data

		print(" [CAL]: Detecting and removing cosmic rays ...")
		crmask, cleanarr = astroscrappy.detect_cosmics(frame_data, inmask=None, sigclip=4.0, satlevel=np.inf, sepmed=False, cleantype="medmask", fsmode="median")

		print(" [CAL]: Converting cleaned array to FITS ...")
		clean_frame = fits.PrimaryHDU(cleanarr)

		print(" [CAL]: Saving FITS to directory", output_dir, "...")
		clean_frame.writeto(output_dir + "/cr-" + str(item), overwrite=True)

	return

if __name__ == "__main__":

	print(" [CAL]: Running [do_cosmicray_detect] as script ...")
	start = time.time()

	print(" [CAL]: Reading configuration file ...")
	config = configparser.ConfigParser()
	config.read("/home/rcamuccio/Documents/CAL/config/config.ini")

	print(" [CAL]: Parsing directory paths ...")
	input_dir = config["do_cosmicray_detect"]["input_dir"]
	output_dir = config["do_cosmicray_detect"]["output_dir"]

	print(" [CAL]: Checking if output path exists ...")
	if not os.path.exists(output_dir):
		print(" [CAL]: Creating output directory", output_dir, "...")
		os.makedirs(output_dir)

	print(" [CAL]: Changing to", input_dir, "as current working directory ...")
	os.chdir(input_dir)

	object_list = []

	for frame in glob.glob("*.fit"):

		if os.path.isfile(str(output_dir) + "/cr-" + str(frame)):
			print(" [CAL]: Cleaned frame of", frame, "already exists ...")
			print(" [CAL]: Skipping cosmic ray detection on frame", frame, "...")

		else:
			print(" [CAL]: Adding", frame, "to detection list ...")
			object_list.append(frame)

	print()
	print(" [CAL]: Running [do_cosmicray_detect] ...")
	print()

	do_cosmicray_detect(object_list, output_dir)

	print()
	print(" [CAL]: Ending [do_cosmicray_detect] ...")
	print()

	end = time.time()
	time = end - start
	print(" End of script.", "%.2f" % time, "seconds to complete.")