# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CAL

The function [do_flat_master] creates a normalized flatfield FITS frame

Args:
	flat_list <class 'list'> : list of FITS file names (each name is <class 'str'>)
	master_dark <class 'astropy.nddata.ccddata.CCDData'> : a master dark FITS frame
	combine_method <class 'str'> : combine list of flats by their overall median or mean (default is median)

Returns:
	flatfield <class 'astropy.nddata.ccddata.CCDData'> : a normalized flatfield FITS frame

Date: 26 Apr 2019
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

def do_flat_master(flat_list, master_dark, combine_method="median"):
	"""Create a normalized flatfield frame from a series of individual flats"""

	if combine_method == "median":
		print(" [CAL]: Combining flats by their median ...")
		combined_flat = ccdproc.combine(flat_list, method="median", unit="adu")

	elif combine_method == "mean":
		print(" [CAL]: Combining flats by their mean ...")
		combined_flat = ccdproc.combine(flat_list, method="mean", unit="adu")

	else:
		print(" [CAL]: Unknown combine method, defaulting to median combine ...")
		print(" [CAL]: Combining flats ...")
		combined_flat = ccdproc.combine(flat_list, method="median", unit="adu")

	print(" [CAL]: Subtracting master dark from combined flat ...")
	master_flat = ccdproc.subtract_dark(combined_flat, master_dark, data_exposure=combined_flat.header["exposure"]*u.second, dark_exposure=master_dark.header["exposure"]*u.second, scale=True)

	print(" [CAL]: Reading master flat data ...")
	master_flat_data = np.asarray(master_flat)

	print(" [CAL]: Normalizing master flat ... ")
	flatfield_data = master_flat_data / np.mean(master_flat_data)

	print(" [CAL]: Converting flatfield data to CCDData ...")
	flatfield = ccdproc.CCDData(flatfield_data, unit="adu")

	return flatfield

if __name__ == "__main__":

	print(" [CAL]: Running [do_flat_master] as script ...")
	start = time.time()

	print(" [CAL]: Reading configuration file ...")
	config = configparser.ConfigParser()
	config.read("/home/rcamuccio/Documents/CAL/config/config.ini")

	print(" [CAL]: Parsing directory paths ...")
	dark_dir = config["do_flat_master"]["input_dir_dark"]
	flat_dir = config["do_flat_master"]["input_dir_flat"]
	output_dir = config["do_flat_master"]["output_dir"]

	print(" [CAL]: Checking if output path exists ...")
	if not os.path.exists(output_dir):
		print(" [CAL]: Creating output directory", output_dir, "...")
		os.makedirs(output_dir)

	print(" [CAL]: Checking if flatfield frame exists ...")
	if os.path.isfile(output_dir + "/flatfield.fit"):
		print(" [CAL]: Reading pre-existing flatfield frame ...")
		flatfield = fits.open(flat_dir + "/flatfield.fit")

	else:
		print(" [CAL]: Opening master dark frame ...")
		master_dark = ccdproc.fits_ccddata_reader(dark_dir + "/master-dark.fit")

		print(" [CAL]: Changing to", flat_dir, "as current working directory ...")
		os.chdir(flat_dir)

		flat_list = []

		for frame in glob.glob("*.fit"):
			print(" [CAL]: Adding", frame, "to flat combine list ...")
			flat_list.append(frame)

		print(" [CAL]: Running [do_flat_master] ...")
		flatfield = do_flat_master(flat_list, master_dark)

		if config["do_flat_master"]["write_flat"] == "yes":
			print(" [CAL]: Writing flatfield to output directory ...")
			ccdproc.fits_ccddata_writer(flatfield, output_dir + "/flatfield.fit")

		elif config["do_flat_master"]["write_flat"] == "no":
			print(" [CAL]: Skipping flatfield write to output directory ...")

		else:
			print(" [CAL]: Unknown command for saving to directory ...")
			print(" [CAL]: Skipping flatfield write to output directory ...")

	end = time.time()
	time = end - start
	print()
	print(" [CAL]: Script [do_flat_master] completed in", "%.2f" % time, "s")