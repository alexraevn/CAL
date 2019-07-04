# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CAL

The function [do_wcs_align] aligns a series of FITS frames to a reference frame via WCS frame

Args:
	object_list <class 'list'> : list of FITS file names (each name is <class 'str'>)
	output_dir <class 'str'> : path to directory for saving aligned FITS files

Returns:
	n/a

---

The function [do_astro_align] aligns a series of FITS frames to a reference frame via ASTROALIGN

Args:
	object_list <class 'list'> : list of FITS file names (each name is <class 'str'>)
	output_dir <class 'str'> : path to directory for saving aligned FITS files

Returns:
	n/a

Date: 27 Apr 2019
Last update: 4 Jul 2019
"""

__author__ = "Richard Camuccio"
__version__ = "1.0"

from astropy import units as u
from astropy.io import fits
from astropy.wcs import WCS
from reproject import reproject_interp
import astroalign as aa
import configparser
import glob
import numpy as np
import os
import time

def do_wcs_align(object_list, output_dir):
	"""Align a series of frames to a reference frame via WCS"""

	if len(object_list) == 0:
		print(" [CAL]: List has zero frames to align ...")

	else:
		print(" [CAL]: Sorting align list ...")
		object_list = sorted(object_list)
		print(" [CAL]: Sorted list:", object_list, "...")

		print(" [CAL]: Opening reference align frame", object_list[0], "...")
		reference_frame = fits.open(object_list[0])

		print(" [CAL]: Reading frame", object_list[0], "data ...")
		reference_data = reference_frame[0].data

		print(" [CAL]: Reading frame", object_list[0], "header ...")
		reference_header = reference_frame[0].header

		print(" [CAL]: Saving align frame", object_list[0], "...")
		reference_frame.writeto(output_dir + "/a-"+str(object_list[0]))

		#if reference_header["CTYPE1"] == "RA---TAN":
		#	reference_header["CTYPE1"] = "RA---TPV"
		#if reference_header["CTYPE2"] == "DEC--TAN":
		#	reference_header["CTYPE2"] = "DEC--TPV"

		#reference_wcs = WCS(reference_header)
		#reference_wcs.wcs.ctype = ["RA---TPV", "DEC--TPV"]

		for i in range(1, len(object_list)):

			print(" [CAL]: Opening frame", object_list[i], "...")
			target_frame = fits.open(object_list[i])

			print(" [CAL]: Reading frame", object_list[i], "data ...")
			target_data = target_frame[0].data

			print(" [CAL]: Reading frame", object_list[i], "header ...")
			target_header = target_frame[0].header

			print(" [CAL]: Aligning target frame with reference frame ...")
			array, footprint = reproject_interp(target_frame, reference_header)

			print(" [CAL]: Writing aligned frame to directory", output_dir, "...")
			fits.writeto(output_dir + "/a-" + str(object_list[i]), array, reference_header, overwrite=True)

	return

def do_astro_align(object_list, output_dir):
	"""Align a series of frames to a reference frame via ASTROALIGN"""

	if len(object_list) == 0:
		print(" [CAL]: List has zero frames to align ...")

	else:
		print(" [CAL]: Sorting align list ...")
		object_list = sorted(object_list)
		print(" [CAL]: Sorted list:", object_list, "...")

		print(" [CAL]: Opening reference align frame", object_list[0], "...")
		reference_frame = fits.open(object_list[0])

		print(" [CAL]: Reading frame", object_list[0], "data ...")
		reference_data = reference_frame[0].data

		print(" [CAL]: Saving reference frame", object_list[0], "...")
		reference_frame.writeto(output_dir + "/a-" + str(object_list[0]))

		for i in range(1, len(object_list)):

			print(" [CAL]: Opening frame", object_list[i], "...")
			target_frame = fits.open(object_list[i])

			print(" [CAL]: Reading frame", object_list[i], "data ...")
			target_data = target_frame[0].data

			print(" [CAL]: Aligning frame", object_list[i], "with reference", object_list[0], "...")
			aligned_data = aa.register(target_data, reference_data)

			print(" [CAL]: Converting frame", object_list[i], "to FITS ...")
			aligned_frame = fits.PrimaryHDU(aligned_data)

			print(" [CAL]: Saving aligned frame", object_list[i], "to directory", output_dir, "...")
			aligned_frame.writeto(output_dir + "/a-" + str(object_list[i]))

	return

if __name__ == "__main__":

	print(" [CAL]: Running [do_align] as script ...")
	start = time.time()

	print(" [CAL]: Reading configuration file ...")
	config = configparser.ConfigParser()
	config.read("/home/rcamuccio/Documents/CAL/config/config.ini")

	print(" [CAL]: Parsing directory paths ...")
	input_dir = config["do_align"]["input_dir"]
	output_dir = config["do_align"]["output_dir"]

	print(" [CAL]: Checking if output path exists ...")
	if not os.path.exists(output_dir):
		print(" [CAL]: Creating output directory", output_dir, "...")
		os.makedirs(output_dir)
	
	print(" [CAL]: Changing to", input_dir, "as current working directory ...")
	os.chdir(input_dir)

	object_list = []

	for frame in glob.glob("*.fit"):

		if os.path.isfile(str(output_dir) + "/a-" + str(frame)):
			print(" [CAL]: Aligned frame of", frame, "already exists ...")
			print(" [CAL]: Skipping align on frame", frame, "...")

		else:
			print(" [CAL]: Adding", frame, "to align list ...")
			object_list.append(frame)

	if config["do_align"]["wcs_align"] == "yes":

		print()
		print(" [CAL]: Running [do_align][do_wcs_align] ...")
		print()

		do_wcs_align(object_list, output_dir)

		print()
		print(" [CAL]: Ending [do_align][do_wcs_align] ...")
		print()

	elif config["do_align"]["wcs_align"] == "no":

		print()
		print(" [CAL]: Running [do_align][do_astro_align] ...")
		print()

		do_astro_align(object_list, output_dir)

		print()
		print(" [CAL]: Ending [do_align][do_astro_align] ...")
		print()

	end = time.time()
	time = end - start
	print(" End of script.", "%.2f" % time, "seconds to complete.")