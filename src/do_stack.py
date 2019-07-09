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
Last update: 7 Jul 2019
"""

__author__ = "Richard Camuccio"
__version__ = "1.1.0"

from astropy import units as u
from astropy.io import fits
import ccdproc
import configparser
import glob
import numpy as np
import os
import time

def do_median_stack(object_list):
	"""Create median stack for series of FITS frames"""

	print(" [CAL][do_stack][do_median_stack]: Creating median stack")
	stack = ccdproc.combine(object_list, method="median", unit="adu")

	return stack

def do_mean_stack(object_list):
	"""Create mean stack for series of FITS frames"""

	print(" [CAL][do_stack][do_mean_stack]: Creating mean stack")
	stack = ccdproc.combine(object_list, method="mean", unit="adu")

	return stack

if __name__ == "__main__":

	os.system("clear")

	print(" [CAL]: Running [do_stack] as script")
	start = time.time()

	print(" [CAL]: Reading configuration file")
	config = configparser.ConfigParser()
	config.read("/home/rcamuccio/Documents/CAL/config/config.ini")

	print(" [CAL]: Parsing directory paths")
	input_dir = config["do_stack"]["input_dir"]
	output_dir = config["do_stack"]["output_dir"]

	print(" [CAL]: Checking if output path exists")
	if not os.path.exists(output_dir):
		print(" [CAL]: Creating output directory", output_dir)
		os.makedirs(output_dir)

	print(" [CAL]: Checking if stack exists")
	if os.path.isfile(output_dir + "/median-stack.fit"):
		print(" [CAL]: Median stack already exists... reading pre-existing stack")
		stack = fits.open(output_dir + "/median-stack.fit")

	else:
		print(" [CAL]: Changing to", input_dir, "as current working directory ...")
		os.chdir(input_dir)

		object_list = []

		for frame in glob.glob("*.fit"):
			print(" [CAL]: Adding", frame, "to stack list")
			object_list.append(frame)

		if config["do_stack"]["stack_method"] == "median":

			print()
			print(" [CAL]: Running [do_stack][do_median_stack]")
			print()

			try:
				stack = do_median_stack(object_list)

				print(" [CAL]: Converting stack data to FITS")
				stack_fits = fits.PrimaryHDU(stack)

				print(" [CAL]: Saving stack to directory", output_dir)
				stack_fits.writeto(output_dir + "/stack.fit", overwrite=True)
				print()

			except MemoryError:
				print(" [CAL]: MEMORY OVERLOAD... skipping stack")

			print()
			print(" [CAL]: Ending [do_stack][do_median_stack]")
			print()

		elif config["do_stack"]["stack_method"] == "mean":

			print()
			print(" [CAL]: Running [do_stack][do_mean_stack]")
			print()

			try:

				stack = do_mean_stack(object_list)

				print(" [CAL]: Converting stack data to FITS")
				stack_fits = fits.PrimaryHDU(stack)

				print(" [CAL]: Saving stack to directory", output_dir)
				stack_fits.writeto(output_dir + "/stack.fit", overwrite=True)
				print()

			except MemoryError:
				print(" [CAL]: MEMORY ERROR... skipping stack")

			print()
			print(" [CAL]: Ending [do_stack][do_mean_stack]")
			print()

	end = time.time()
	time = end - start
	print(" End of script.", "%.2f" % time, "seconds to complete.")