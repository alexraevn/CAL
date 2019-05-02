# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Richard Camuccio
# 27 Apr 2019
#
# Last update: 28 Apr 2019
#
# Function: do_align (CAL)
#

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

print("<STATUS> Reading configuration file ...")
config = configparser.ConfigParser()
config.read("/home/rcamuccio/Documents/CAL/config.ini")

def do_align(object_list, input_dir, output_dir):
	"""Align a series of frames to a reference frame via WCS or ASTROALIGN"""

	if config["do_align"]["wcs"] == "yes":

		# Sort object list
		print("<STATUS> Sorting align list ...")
		object_list = sorted(object_list)
		print("<STATUS> Sorted list:", object_list, "...")

		# Create reference align frame
		print("<STATUS> Opening reference align frame", object_list[0], "...")
		reference_frame = fits.open(object_list[0])

		# Read reference align frame data
		print("<STATUS> Reading frame", object_list[0], "data ...")
		reference_data = reference_frame[0].data
		reference_header = reference_frame[0].header

		# Save reference align frame to align directory
		if os.path.isfile(str(output_dir) + "/a-" + str(object_list[0])):

			print("<STATUS> Skipping save for reference align frame", object_list[0], "...")

		else:

			print("<STATUS> Saving align frame", object_list[0], "...")
			reference_frame.writeto(output_dir + "/a-"+str(object_list[0]))

		#if reference_header["CTYPE1"] == "RA---TAN":
		#	reference_header["CTYPE1"] = "RA---TPV"
		#if reference_header["CTYPE2"] == "DEC--TAN":
		#	reference_header["CTYPE2"] = "DEC--TPV"

		#reference_wcs = WCS(reference_header)
		#reference_wcs.wcs.ctype = ["RA---TPV", "DEC--TPV"]

		for i in range(1, len(object_list)):

			if os.path.isfile(str(output_dir) + "/a-" + str(object_list[i])):

				print("<STATUS> Skipping align on frame", str(object_list[i]), "...")

			else:

				print("<STATUS> Opening frame", object_list[i], "...")
				target_frame = fits.open(object_list[i])

				print("<STATUS> Reading frame", object_list[i], "data ...")
				target_data = target_frame[0].data
				target_header = target_frame[0].header

				array, footprint = reproject_interp(target_frame, reference_header)

				if config["do_align"]["write_align"] == "yes":

					fits.writeto(output_dir + "/a-" + str(object_list[i]), array, reference_header, overwrite=True)

				else:

					pass

	else:

		# Sort object list
		print("<STATUS> Sorting align list ...")
		object_list = sorted(object_list)
		print("<STATUS> Sorted list:", object_list, "...")

		# Create reference align frame
		print("<STATUS> Opening reference align frame", object_list[0], "...")
		reference_frame = fits.open(object_list[0])

		# Read reference align frame data
		print("<STATUS> Reading frame", object_list[0], "data ...")
		reference_data = reference_frame[0].data

		# Save reference align frame to align directory
		if os.path.isfile(str(output_dir) + "/a-" + str(object_list[0])):

			print("<STATUS> Skipping save for reference align frame", object_list[0], "...")

		else:

			print("<STATUS> Saving align frame", object_list[0], "...")
			reference_frame.writeto(output_dir + "/a-"+str(object_list[0]))

		# Align frames to reference align frame
		for i in range(1, len(object_list)):

			if os.path.isfile(str(output_dir) + "/a-" + str(object_list[i])):

				print("<STATUS> Skipping align on frame", str(object_list[i]), "...")

			else:

				print("<STATUS> Opening frame", object_list[i], "...")
				target_frame = fits.open(object_list[i])

				print("<STATUS> Reading frame", object_list[i], "data ...")
				target_data = target_frame[0].data

				print("<STATUS> Aligning frame", object_list[i], "with", str(object_list[0]), "...")
				aligned_data = aa.register(target_data, reference_data)

				print("<STATUS> Converting frame", object_list[i], "to FITS format ...")
				aligned_frame = fits.PrimaryHDU(aligned_data)

				print("<STATUS> Saving aligned frame", object_list[i], "to directory", output_dir, "...")
				aligned_frame.writeto(output_dir + "/a-" + str(object_list[i]))

	return

if __name__ == "__main__":

	start = time.time()

	input_dir = config["do_align"]["input_dir"]
	output_dir = config["do_align"]["output_dir"]
	object_list = []

	if not os.path.exists(output_dir):

   		os.makedirs(output_dir)

	os.chdir(input_dir)
	print("<STATUS> Changing to", input_dir, "as current working directory ...")

	for frame in glob.glob("*.fit"):

		print("<STATUS> Adding", frame, "to align list ...")
		object_list.append(frame)

	print("<STATUS> Running [do_align] ...")
	do_align(object_list, input_dir, output_dir)

	end = time.time()
	time = end - start
	print()
	print("%.2f" % time, "seconds to complete.")