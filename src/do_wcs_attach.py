# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CAL

The function [do_wcs_attach] Create a series of WCS-attached FITS frames using local Astrometry.net

Args:
	object_list <class 'list'> : list of FITS file names (each name is <class 'str'>)
	output_dir <class 'str'> : path for saving solved FITS files
	search <class 'None'> or <class 'list'> : list containing RA "hh:mm:ss.ss", Dec "(-)dd:mm:ss.ss", and radius (all are <class 'str'>); default is None

Returns:
	n/a

Date: 2 May 2019
Last update: 17 Jul 2019
"""

__author__ = "Richard Camuccio"
__version__ = "1.2.0"

from astropy.io import fits
import configparser
import glob
import os
import subprocess
import time

def do_wcs_attach(object_list, output_dir, search=None):
	"""Create WCS-attached FITS to series of frames using astrometry.net"""

	for item in object_list:

		print(" [CAL][do_wcs_attach]: Parsing file names")
		file = item[:-4]
		file_axy = file + ".axy"
		file_corr = file + ".corr"
		file_match = file + ".match"
		file_new = file + ".new"
		file_rdls = file + ".rdls"
		file_solved = file + ".solved"
		file_wcs = file + ".wcs"
		file_xyls = file + "-indx.xyls"

		if search == None:

			print()
			print(" [CAL][do_wcs_attach]: Running astrometry.net code on", item)
			subprocess.run(["solve-field", "--no-plots", item])
		else:

			ra = search[0]
			dec = search[1]
			radius = search[2]

			print()
			print(" [CAL][do_wcs_attach]: Running astrometry.net code on", item)
			subprocess.run(["solve-field", "--no-plots", item, "--ra", ra, "--dec", dec, "--radius", radius])
		
		print(" [CAL][do_wcs_attach]: Cleaning up")
		subprocess.run(["rm", file_axy])
		subprocess.run(["rm", file_corr])
		subprocess.run(["rm", file_match])
		subprocess.run(["rm", file_rdls])
		subprocess.run(["rm", file_solved])
		subprocess.run(["rm", file_wcs])
		subprocess.run(["rm", file_xyls])

		print(" [CAL][do_wcs_attach]: Moving solved fields to", output_dir)
		subprocess.run(["mv", file_new, output_dir + str("/wcs-") + file + ".fit"])
		print()

	return

if __name__ == "__main__":

	os.system("clear")

	print(" Running CAL")
	print()
	print(" [CAL]: Running [do_wcs_attach] as script")
	start = time.time()

	print(" [CAL]: Reading configuration file")
	config = configparser.ConfigParser()
	config.read("/home/rcamuccio/Documents/CAL/config/config.ini")

	print(" [CAL]: Parsing directory paths")
	input_dir = config["do_wcs_attach"]["input_dir"]
	output_dir = config["do_wcs_attach"]["output_dir"]

	print(" [CAL]: Checking if output path exists")
	if not os.path.exists(output_dir):
		print(" [CAL]: Creating output directory", output_dir)
		os.makedirs(output_dir)

	print(" [CAL]: Changing to", input_dir, "as current working directory")
	os.chdir(input_dir)

	object_list = []

	for frame in glob.glob("*.fit"):

		if os.path.isfile(str(output_dir) + "/c-" + str(frame)):
			print(" [CAL]: WCS-solved frame of", frame, "already exists")
			print(" [CAL]: Skipping calibration on frame", frame)

		else:
			print(" [CAL]: Adding", frame, "to solve list")
			object_list.append(frame)

	print(" [CAL]: Sorting object list")
	object_list = sorted(object_list)

	print()
	print(" [CAL]: Running [do_wcs_attach]")
	do_wcs_attach(object_list, output_dir)
	print(" [CAL]: Ending [do_wcs_attach]")
	print()

	end = time.time()
	time = end - start
	print(" End of script.", "%.2f" % time, "seconds to complete.")