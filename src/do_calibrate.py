# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Richard Camuccio
# 27 Apr 2019
#
# Last update: 27 Apr 2019
#
# Function: do_calibrate (CAL)
#

from astropy import units as u
from astropy.io import fits
import ccdproc
import configparser
import glob
import numpy as np
import os
import time

print("<STATUS> Reading configuration file ...")
config = configparser.ConfigParser()
config.read("/home/rcamuccio/Documents/CAL/config.ini")

def do_calibrate(object_list, master_dark, flatfield, object_dir, dark_dir, flat_dir, output_dir):
	"""Calibrate a series of object frames with a master dark and flatfield"""

	for item in object_list:

		if os.path.isfile(str(output_dir) + "/cal-" + str(item)):

			print("<STATUS> Skipping calibration on frame", item, "...")

		else:

			print("<STATUS> Reading", item, "data ...")
			object_frame = ccdproc.fits_ccddata_reader(item, unit="adu")

			print("<STATUS> Subtracting master dark from", item, "...")
			object_min_dark = ccdproc.subtract_dark(object_frame, master_dark, data_exposure=object_frame.header["exposure"]*u.second, dark_exposure=master_dark.header["exposure"]*u.second, scale=True)

			print("<STATUS> Dividing", item, "by flatfield ...")
			cal_object_frame = ccdproc.flat_correct(object_min_dark, flatfield)

			if config["do_calibrate"]["write_cal"] == "yes":

				print("<STATUS> Saving frame", item, "...")
				ccdproc.fits_ccddata_writer(cal_object_frame, str(output_dir) + "/cal-" + str(item))

	return

if __name__ == "__main__":

	start = time.time()

	object_dir = config["do_calibrate"]["input_dir_obj"]
	dark_dir = config["do_calibrate"]["input_dir_dark"]
	flat_dir = config["do_calibrate"]["input_dir_flat"]
	output_dir = config["do_calibrate"]["output_dir"]
	object_list = []

	if not os.path.exists(output_dir):
   		os.makedirs(output_dir)

	master_dark = ccdproc.fits_ccddata_reader(dark_dir + "/master-dark.fit")
	flatfield = ccdproc.fits_ccddata_reader(flat_dir + "/flatfield.fit")

	os.chdir(object_dir)
	print("<STATUS> Changing to", object_dir, "as current working directory ...")

	for frame in glob.glob("*.fit"):

		print("<STATUS> Adding", frame, "to calibration list ...")
		object_list.append(frame)

	print("<STATUS> Running [do_calibrate] ...")
	do_calibrate(object_list, master_dark, flatfield, object_dir, dark_dir, flat_dir, output_dir)

	end = time.time()
	time = end - start
	print()
	print("%.2f" % time, "seconds to complete.")