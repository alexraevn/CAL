# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CAL

The function [do_dark_master] creates a master dark FITS frame

Args:
	dark_list <class 'list'> : list of FITS file names (each name is <class 'str'>)
	combine_method <class 'str'> : combine list of darks by their overall median or mean (default is median)

Returns:
    master_dark <class 'astropy.nddata.ccddata.CCDData'> : a master dark FITS frame

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

def do_dark_master(dark_list, combine_method="median"):
	"""Create a master dark frame from a series of individual darks"""

	if combine_method == "median":
		print(" [CAL]: Combining darks by their median ...")
		master_dark = ccdproc.combine(dark_list, method="median", unit="adu")

	elif combine_method == "mean":
		print(" [CAL]: Combining darks by their mean ...")
		master_dark = ccdproc.combine(dark_list, method="mean", unit="adu")

	else:
		print(" [CAL]: Unknown combine method, defaulting to median combine ...")
		print(" [CAL]: Combining darks ...")
		master_dark = ccdproc.combine(dark_list, method="median", unit="adu")

	return master_dark

if __name__ == "__main__":

	os.system("clear")

	print(" Running CAL ...")
	print()
	print(" [CAL]: Running [do_dark_master] as script ...")
	start = time.time()

	print(" [CAL]: Reading configuration file ...")
	config = configparser.ConfigParser()
	config.read("/home/rcamuccio/Documents/CAL/config/config.ini")

	print(" [CAL]: Parsing directory paths ...")
	input_dir = config["do_dark_master"]["input_dir"]
	output_dir = config["do_dark_master"]["output_dir"]

	print(" [CAL]: Checking if output path exists ...")
	if not os.path.exists(output_dir):
		print(" [CAL]: Creating output directory", output_dir, "...")
		os.makedirs(output_dir)

	print(" [CAL]: Checking if master dark frame exists ...")
	if os.path.isfile(output_dir + "/master-dark.fit"):
		print(" [CAL]: Reading pre-existing master dark frame ...")
		master_dark = fits.open(output_dir + "/master-dark.fit")

	else:
		print(" [CAL]: Changing to", input_dir, "as current working directory ...")
		os.chdir(input_dir)

		dark_list = []

		for frame in glob.glob("*.fit"):
			print(" [CAL]: Adding", frame, "to dark combine list ...")
			dark_list.append(frame)

		print()
		print(" [CAL]: Running [do_dark_master] ...")
		print()

		master_dark = do_dark_master(dark_list)
		
		print()
		print(" [CAL]: Ending [do_dark_master] ...")
		print()

		print(" [CAL]: Writing master dark to output directory ...")
		ccdproc.fits_ccddata_writer(master_dark, output_dir + "/master-dark.fit")

	end = time.time()
	time = end - start
	print(" End of script.", "%.2f" % time, "seconds to complete.")