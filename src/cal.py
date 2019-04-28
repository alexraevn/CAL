# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Richard Camuccio
# 11 Mar 2019
#
# Last update: 27 Apr 2019
#
# CTMO Analysis Library
#

from astropy import units as u
from astropy.io import fits
import astroalign as aa
import ccdproc
import configparser
import os
import numpy as np

print("<STATUS:CAL> Reading configuration file ...")
config = configparser.ConfigParser()
config.read("/home/rcamuccio/Documents/CAL/config.ini")

def do_astro_align(object_list, directory):
	"""Align a series of frames to a reference frame via ASTROALIGN"""

	# Sort object list
	print("<STATUS:CAL> Sorting align list ...")
	object_list = sorted(object_list)
	print("<STATUS:CAL> Sorted list:", object_list, "...")

	# Create reference align frame
	print("<STATUS:CAL> Opening reference align frame", object_list[0], "...")
	reference_frame = fits.open(object_list[0])

	# Read reference align frame data
	print("<STATUS:CAL> Reading frame", object_list[0], "data ...")
	reference_data = reference_frame[0].data

	# Save reference align frame to align directory
	if os.path.isfile(str(directory) + "/a-" + str(object_list[0])):
		print("<STATUS:CAL> Skipping save for reference align frame", object_list[0], "...")

	else:
		print("<STATUS:CAL> Saving align frame", object_list[0], "...")
		reference_frame.writeto(directory + "/a-"+str(object_list[0]))

	# Align frames to reference align frame
	for i in range(1, len(object_list)):

		if os.path.isfile(str(directory) + "/a-" + str(object_list[i])):
			print("<STATUS:CAL> Skipping align on frame", str(object_list[i]), "...")

		else:
			print("<STATUS:CAL> Opening frame", object_list[i], "...")
			target_frame = fits.open(object_list[i])

			print("<STATUS:CAL> Reading frame", object_list[i], "data ...")
			target_data = target_frame[0].data

			print("<STATUS:CAL> Aligning frame", object_list[i], "with", str(object_list[0]), "...")
			aligned_data = aa.register(target_data, reference_data)

			print("<STATUS:CAL> Converting frame", object_list[i], "to FITS format ...")
			aligned_frame = fits.PrimaryHDU(aligned_data)

			print("<STATUS:CAL> Saving aligned frame", object_list[i], "to directory", directory, "...")
			aligned_frame.writeto(directory + "/a-" + str(object_list[i]))
	
	return

def do_wcs_align():
	"""Align a series of WCS-attached frames"""

	return

def do_cosmicray_detect():
	"""Detect and remove cosmic rays from a series of frames"""

	return

def do_calibrate(object_list, master_dark, flatfield, directory):
	"""Calibrate a series of object frames with a master dark and flatfield"""

	for item in object_list:

		# Check for pre-existing calibrated frame
		if os.path.isfile(str(directory) + "/cal-" + str(item)):

			print("<STATUS:CAL> Skipping calibrate on frame", item, "...")

		else:

			print("<STATUS:CAL> Reading", item, "data ...")
			object_frame = ccdproc.fits_ccddata_reader(item, unit="adu")

			print("<STATUS:CAL> Subtracting master dark from", item, "...")
			object_min_dark = ccdproc.subtract_dark(object_frame, master_dark, data_exposure=object_frame.header["exposure"]*u.second, dark_exposure=master_dark.header["exposure"]*u.second, scale=True)

			print("<STATUS:CAL> Dividing", item, "by flatfield ...")
			cal_object_frame = ccdproc.flat_correct(object_min_dark, flatfield)

			print("<STATUS:CAL> Saving frame", item, "...")
			ccdproc.fits_ccddata_writer(cal_object_frame, str(directory) + "/cal-" + str(item))

	return

def do_dark_master(dark_list):
	"""Create a master dark frame"""

	print("<STATUS:CAL> Combining darks ...")
	master_dark = ccdproc.combine(dark_list, method="median", unit="adu")

	return master_dark

def do_flat_master(flat_list, master_dark, input_dir, output_dir):
	"""Create a normalized flatfield frame"""

	print("<STATUS:CAL> Combining flats ...")

	if config["main"]["flat_combine"] == "median":

		combined_flat = ccdproc.combine(flat_list, method="median", unit="adu")

	elif config["main"]["flat_combine"] == "mean":

		combined_flat = ccdproc.combine(flat_list, method="mean", unit="adu")

	print("<STATUS:CAL> Subtracting dark from combined flat ...")
	master_flat = ccdproc.subtract_dark(combined_flat, master_dark, data_exposure=combined_flat.header["exposure"]*u.second, dark_exposure=master_dark.header["exposure"]*u.second, scale=True)

	print("<STATUS:CAL> Reading master flat data ...")
	master_flat_data = np.asarray(master_flat)

	print("<STATUS:CAL> Normalizing master flat ... ")

	if config["main"]["flat_normalization"] == "median":

		flatfield_data = master_flat_data / np.median(master_flat_data)

	elif config["main"]["flat_normalization"] == "mean":

		flatfield_data = master_flat_data / np.mean(master_flat_data)

	flatfield = fits.PrimaryHDU(flatfield_data)

	if config["main"]["write_flat"] == "yes":

		flatfield.writeto(directory + "/flatfield.fit")

	elif config["main"]["write_flat"] == "no":

		pass

	return flatfield, flatfield_data

def do_sextractor():
	"""Perform source extraction on series of frames via SExtractor"""

	return

def do_daofind():
	"""Perform source extraction on series of frames via DAOStarFinder"""

	return

def do_dss_search():
	"""Retrieve DSS field"""

	return

def do_wcs_attach():
	"""Plate solve series of frames"""

	return

def do_stack(object_list, directory):
	"""Create median-combined stack"""

	print("<STATUS:CAL> Combining frames ...")
	stack = ccdproc.combine(object_list, method="median", unit="adu")

	print("<STATUS:CAL> Converting stack data to FITS format ...")
	fits_stack = fits.PrimaryHDU(stack)

	print("<STATUS:CAL> Saving stack to directory", directory, "...")
	fits_stack.writeto(directory + "/stack.fit", overwrite=True)

	return stack

def do_background_sub():
	"""Perform background estimation and subtraction on series of frames"""

	return

def do_field_sub():
	"""Subtract target and reference frames"""

	return

def do_galaxy_sub():
	"""Model and subtract galaxy from frame"""

	return

def do_tofu_nav(input_dir):
	"""Define location of directories related to TOFU script"""

	# Target and reference subdirectories
	tar_dir = str(input_dir) + "Target"
	print()
	print("<STATUS:CAL> Target directory:", tar_dir, "...")

	ref_dir = str(input_dir) + "Reference"
	print("<STATUS:CAL> Reference directory:", ref_dir, "...")
	print()

	tar_obj_dir, tar_dark_dir, tar_flat_dir = [], [], []
	ref_obj_dir, ref_dark_dir, ref_flat_dir = [], [], []

	# Populate cal and obj (tar) directory lists
	for sub_dir in os.listdir(tar_dir):

		if os.path.isdir(os.path.join(tar_dir, sub_dir)):

			if "dark" in sub_dir:
				tar_dark_dir.append(os.path.join(tar_dir, sub_dir))

			elif "flat" in sub_dir:
				tar_flat_dir.append(os.path.join(tar_dir, sub_dir))

			else:
				tar_obj_dir.append(os.path.join(tar_dir, sub_dir))

	print()
	print("<STATUS:CAL> Target object directories:", tar_obj_dir, "...")
	print("<STATUS:CAL> Target dark directory:", tar_dark_dir, "...")
	print("<STATUS:CAL> Target flat directory:", tar_flat_dir, "...")
	print()

	# Populate cal and obj (ref) directory lists
	for sub_dir in os.listdir(ref_dir):

		if os.path.isdir(os.path.join(ref_dir, sub_dir)):

			if "dark" in sub_dir:
				ref_dark_dir.append(os.path.join(ref_dir, sub_dir))

			elif "flat" in sub_dir:
				ref_flat_dir.append(os.path.join(ref_dir, sub_dir))

			else:
				ref_obj_dir.append(os.path.join(ref_dir, sub_dir))

	print()
	print("<STATUS:CAL> Reference object directories:", ref_obj_dir, "...")
	print("<STATUS:CAL> Reference dark directory:", ref_dark_dir, "...")
	print("<STATUS:CAL> Reference flat directory:", ref_flat_dir, "...")
	print()

	return tar_obj_dir, tar_dark_dir, tar_flat_dir, ref_obj_dir, ref_dark_dir, ref_flat_dir

def do_tsp_nav():
	"""Define location of directories related to TSP script"""

	return