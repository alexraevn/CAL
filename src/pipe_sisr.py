# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CAL

SISR is the Static Image Series Reduction pipeline

Date: 9 Jul 2019
Last update: 17 Jul 2019
"""

__author__ = "Richard Camuccio"
__version__ = "1.2.0"

from do_align import *
from do_calibrate import *
from do_dark_master import *
from do_flat_master import *
from do_read import *
from do_wcs_attach import *
from astropy.io import fits
import ccdproc
import configparser
import glob
import os
import time

os.system("clear")

print(" [CAL]: Starting SISR")
print()
start = time.time()

print(" [CAL][SISR]: Reading configuration file")
config = configparser.ConfigParser()
config.read("../config/script.ini")

input_dir = config["sisr"]["input_dir"]
print(" [CAL][SISR]: Input directory:", input_dir)

object_dir_list = []
dark_list = []
flat_list = []

for directory in os.listdir(input_dir):

	# Create master darks

	if directory == "dark":
		dark_dir = input_dir + "/" + directory
		print(" [CAL][SISR]: Dark directory is", dark_dir)

		for sub_directory in os.listdir(dark_dir):
			dark_sub_dir = input_dir + "/dark/" + sub_directory
			
			print(" [CAL][SISR]: Changing to", dark_sub_dir)
			os.chdir(dark_sub_dir)

			if os.path.isfile(str(dark_sub_dir) + "/master-dark.fit"):
				print(" [CAL][SISR]: Master dark in", dark_sub_dir, "exists")

			else:
				print(" [CAL][SISR]: Reading dark frames in", dark_sub_dir)
				for frame in glob.glob("*.fit"):
					dark_list.append(frame)
				
				print()
				print(" [CAL][SISR]: Running [do_dark_master]")
				master_dark = do_dark_master(dark_list, combine_method="median")
				print(" [CAL][SISR]: Finished [do_dark_master]")
				print()

				print(" [CAL][SISR]: Writing master-dark.fit to", dark_sub_dir)
				ccdproc.fits_ccddata_writer(master_dark, dark_sub_dir + "/master-dark.fit")

	# Create flatfield

	elif directory == "flat":
		flat_dir = input_dir + "/" + directory
		print(" [CAL][SISR]: Flat directory is", flat_dir)

		for sub_directory in os.listdir(flat_dir):
			flat_sub_dir = input_dir + "/flat/" + sub_directory

			print(" [CAL][SISR]: Changing to", flat_sub_dir)
			os.chdir(flat_sub_dir)

			if os.path.isfile(str(flat_sub_dir) + "/flatfield.fit"):
				print(" [CAL][SISR]: Flatfield in", flat_sub_dir, "exists")

			else:
				print(" [CAL][SISR]: Reading flat frames in", flat_sub_dir)
				for frame in glob.glob("*.fit"):
					flat_list.append(frame)

				print(" [CAL][SISR]: Matching flat exposure time with master dark exposure time")
				test_frame = fits.open(flat_list[0])
				exptime = test_frame[0].header["EXPTIME"]
				exptime_int = int(exptime)

				master_dark_dir = dark_dir + "/" + str(exptime_int) + "/master-dark.fit"
				print(" [CAL][SISR]: Reading master-dark.fit from", master_dark_dir)
				master_dark = ccdproc.fits_ccddata_reader(master_dark_dir)
				
				print()
				print(" [CAL][SISR]: Running [do_flat_master]")
				flatfield = do_flat_master(flat_list, master_dark, combine_method="median")
				print(" [CAL][SISR]: Finished [do_flat_master]")
				print()

				print(" [CAL][SISR]: Writing flatfield.fit to", flat_sub_dir)
				ccdproc.fits_ccddata_writer(flatfield, flat_sub_dir + "/flatfield.fit")

	else:
		object_dir = input_dir + "/" + directory
		object_dir_list.append(object_dir)

for directory in object_dir_list:

	print(" [CAL][SISR]: Changing to", directory)
	os.chdir(directory)

	cal_directory = directory + "/cal"
	if not os.path.exists(cal_directory):
		print(" [CAL][SISR]: Creating directory", cal_directory)
		os.makedirs(cal_directory)
	else:
		print(" [CAL][SISR]: Directory", cal_directory, "already exists")

	raw_directory = directory + "/raw"
	if not os.path.exists(raw_directory):
		print(" [CAL][SISR]: Creating directory", raw_directory)
		os.makedirs(raw_directory)
	else:
		print(" [CAL][SISR]: Directory", raw_directory, "already exists")

	rej_directory = directory + "/rej"
	if not os.path.exists(rej_directory):
		print(" [CAL][SISR]: Creating directory", rej_directory)
		os.makedirs(rej_directory)
	else:
		print(" [CAL][SISR]: Directory", rej_directory, "already exists")

	print(" [CAL][SISR]: Moving object frames to", raw_directory)
	for frame in glob.glob("*.fit"):
		os.rename(directory + "/" + frame, raw_directory + "/" + frame)

	# Calibrate objects

	print(" [CAL][SISR]: Beginning calibration")
	os.chdir(raw_directory)

	object_list = []

	for frame in glob.glob("*.fit"):

		if os.path.isfile(cal_directory + "/c-" + frame):
			print(" [CAL][SISR]: Skipping calibration on", frame)

		else:
			print(" [CAL][SISR]: Adding", frame, "to calibration list")
			object_list.append(frame)

	print(" [CAL][SISR]: Sorting object list")
	object_list = sorted(object_list)

	if len(object_list) == 0:
		print(" [CAL][SISR]: No frames remaining to calibrate")

	else:
		print(" [CAL][SISR]: Obtaining exposure time from header")
		test_frame = fits.open(object_list[0])
		exptime = test_frame[0].header["EXPTIME"]
		exptime_int = int(exptime)

		master_dark_dir = dark_dir + "/" + str(exptime_int) + "/master-dark.fit"
		
		master_dark = fits.open(master_dark_dir)
		master_dark_data = master_dark[0].data

		flatfield = fits.open(flat_sub_dir + "/flatfield.fit")
		flatfield_data = flatfield[0].data

		print()
		print(" [CAL][SISR]: Running [do_calibrate]")
		do_calibrate(object_list, master_dark_data, flatfield_data, cal_directory)
		print(" [CAL][SISR]: Finished [do_calibrate]")
		print()

	# Plate solve objects

	os.chdir(cal_directory)

	wcs_directory = cal_directory + "/wcs"
	if not os.path.exists(wcs_directory):
		print(" [CAL][SISR]: Creating directory", wcs_directory)
		os.makedirs(wcs_directory)
	else:
		print(" [CAL][SISR]: Directory", wcs_directory, "already exists")

	object_list = []

	for frame in glob.glob("*.fit"):

		if os.path.isfile(wcs_directory + "/wcs-" + frame):
			print(" [CAL][SISR]: Skipping plate solve on", frame)

		else:
			print(" [CAL][SISR]: Adding", frame, "to plate solve list")
			object_list.append(frame)

	object_list = sorted(object_list)

	if len(object_list) == 0:
		print(" [CAL][SISR]: No frames remaining to plate solve")

	else:
		print()
		print(" [CAL][SISR]: Running [do_wcs_attach]")
		do_wcs_attach(object_list, wcs_directory, search=["16:37:16.00", "7:11:00.0", "1"])
		print(" [CAL][SISR]: Finished [do_wcs_attach]")
		print()

	# Align objects

	print(" [CAL][SISR]: Beginning alignment process")
	os.chdir(wcs_directory)

	print(" [CAL][SISR]: Checking directory structure")
	align_directory = wcs_directory + "/align"

	if not os.path.exists(align_directory):
		print(" [CAL][SISR]: Creating directory", align_directory)
		os.makedirs(align_directory)

	else:
		print(" [CAL][SISR]: Directory", align_directory, "already exists")

	object_list = []

	for frame in glob.glob("*.fit"):

		if os.path.isfile(align_directory + "/a-" + frame):
			print(" [CAL][SISR]: Skipping alignment on", frame)

		else:
			print(" [CAL][SISR]: Adding", frame, "to alignment list")
			object_list.append(frame)

	if len(object_list) == 0:
		print(" [CAL][SISR]: No frames remaining to plate solve")

	else:
		object_list = sorted(object_list)

		print()
		print(" [CAL][SISR]: Running [do_align][do_wcs_align]")
		do_wcs_align(object_list, align_directory)
		print(" [CAL][SISR]: Finished [do_align][do_wcs_align]")
		print()

end = time.time()
time = end - start
print()
print(" End of script.", "%.3f" % time, "seconds to complete.")