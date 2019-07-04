# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CAL

The function [do_stack] creates a stack from a series of FITS frames

Args:
	object_list <class 'list'> : list of FITS file names (each name is <class 'str'>)
	stack_method <class 'str'> : combine list of frames by their overall median or mean (default is median)

Returns:
	stack <class 'astropy.nddata.ccddata.CCDData'> : a stacked FITS frame

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

def do_stack(object_list, stack_method="median"):
	"""Create stack of FITS frames"""

	if stack_method == "median":
		print(" [CAL]: Combining frames to create median stack ...")
		stack = ccdproc.combine(object_list, method="median", unit="adu")

	elif stack_method == "mean":
		print(" [CAL]: Combining frames to create mean stack ...")
		stack = ccdproc.combine(object_list, method="mean", unit="adu")

	else:
		print(" [CAL]: Unknown combine method, defaulting to median combine ...")
		print(" [CAL]: Stacking frames ...")
		stack = ccdproc.combine(object_list, method="median", unit="adu")

	return stack

if __name__ == "__main__":

	os.system("clear")

	print(" [CAL]: Running [do_stack] as script ...")
	start = time.time()

	print(" [CAL]: Reading configuration file ...")
	config = configparser.ConfigParser()
	config.read("/home/rcamuccio/Documents/CAL/config/config.ini")

	print(" [CAL]: Parsing directory paths ...")
	input_dir = config["do_stack"]["input_dir"]
	output_dir = config["do_stack"]["output_dir"]

	print(" [CAL]: Checking if output path exists ...")
	if not os.path.exists(output_dir):
		print(" [CAL]: Creating output directory", output_dir, "...")
		os.makedirs(output_dir)

	print(" [CAL]: Checking if stack exists ...")
	if os.path.isfile(output_dir + "/stack.fit"):
		print(" [CAL]: Stack already exists. Reading pre-existing stack ...")
		stack = fits.open(output_dir + "/stack.fit")

	else:
		print(" [CAL]: Changing to", input_dir, "as current working directory ...")
		os.chdir(input_dir)

		object_list = []

		for frame in glob.glob("*.fit"):
			print(" [CAL]: Adding", frame, "to stack list ...")
			object_list.append(frame)

		print()
		print(" [CAL]: Running [do_stack] ...")
		print()

		stack = do_stack(object_list, input_dir, output_dir)

		print()
		print(" [CAL]: Ending [do_stack] ...")
		print()

		print(" [CAL]: Converting stack data to FITS format ...")
		stack_fits = fits.PrimaryHDU(stack)

		print(" [CAL]: Saving stack to directory", output_dir, "...")
		stack_fits.writeto(output_dir + "/stack.fit", overwrite=True)

	end = time.time()
	time = end - start
	print(" End of script.", "%.2f" % time, "seconds to complete.")