# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CAL

The function [do_dark_master] creates a master dark FITS file

Args:
	dark_list <class 'list'> : list of FITS file names (each name is <class 'str'>)
	input_dir <class 'str'> : path to directory of dark frames
	output_dir <class 'str'> : path to directory for saving master dark frame

Returns:
    master_dark <class 'astropy.nddata.ccddata.CCDData'>: A master dark FITS frame

Date: 27 Apr 2019
Last update: 23 Jun 2019
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

print("[CAL]: Reading configuration file ...")
config = configparser.ConfigParser()
config.read("/home/rcamuccio/Documents/CAL/config/config.ini")

def do_dark_master(dark_list, input_dir, output_dir):
	"""Create a master dark frame from a series of individual darks"""

	print("[CAL]: Combining darks ...")

	if config["do_dark_master"]["dark_combine"] == "median":
		master_dark = ccdproc.combine(dark_list, method="median", unit="adu")

	elif config["do_dark_master"]["dark_combine"] == "mean":
		master_dark = ccdproc.combine(dark_list, method="mean", unit="adu")

	if config["do_dark_master"]["write_dark"] == "yes":

		print("[CAL]: Writing master dark to output directory ...")
		ccdproc.fits_ccddata_writer(master_dark, output_dir + "/master-dark.fit")

	elif config["do_dark_master"]["write_dark"] == "no":
		print("[CAL]: Skipping master dark write to output directory ...")

	return master_dark

if __name__ == "__main__":

	print("[CAL]: Running [do_dark_master] as script ...")
	start = time.time()

	print("[CAL]: Parsing directory paths ...")
	input_dir = config["do_dark_master"]["input_dir"]
	output_dir = config["do_dark_master"]["output_dir"]
	dark_list = []

	if os.path.isfile(output_dir + "/master-dark.fit"):

		print("[CAL]: Reading pre-existing master dark frame ...")
		master_dark = fits.open(output_dir + "/master-dark.fit")

	else:

		print("[CAL]: Changing to", input_dir, "as current working directory ...")
		os.chdir(input_dir)

		for frame in glob.glob("*.fit"):

			print("[CAL]: Adding", frame, "to dark combine list ...")
			dark_list.append(frame)

		print("[CAL]: Running [do_dark_master] ...")
		master_dark = do_dark_master(dark_list, input_dir, output_dir)

	end = time.time()
	time = end - start
	print()
	print("[CAL]: Script [do_dark_master] completed in", "%.2f" % time, "s")