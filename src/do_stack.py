# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Richard Camuccio
# 27 Apr 2019
#
# Last update: 27 Apr 2019
#
# Function: do_stack (CAL)
#

from astropy import units as u
from astropy.io import fits
import ccdproc
import configparser
import glob
import numpy as np
import os
import time

print("<STATUS> Reading configuration file ...")
config = configparser.ConfigParser()
config.read("/home/rcamuccio/Documents/CAL/config.ini")

def do_stack(object_list, input_dir, output_dir):
	"""Create stack of FITS frames"""

	if config["do_stack"]["stack_method"] == "median":

		print("<STATUS> Combining frames to create median stack ...")
		stack = ccdproc.combine(object_list, method="median", unit="adu")

	elif config["do_stack"]["stack_method"] == "mean":

		print("<STATUS> Combining frames to create mean stack ...")
		stack = ccdproc.combine(object_list, method="median", unit="adu")

	print("<STATUS> Converting stack data to FITS format ...")
	fits_stack = fits.PrimaryHDU(stack)

	if config["do_stack"]["write_stack"] == "yes":

		print("<STATUS> Saving stack to directory", output_dir, "...")
		fits_stack.writeto(output_dir + "/stack.fit", overwrite=True)

	return stack

if __name__ == "__main__":

	start = time.time()

	input_dir = config["do_stack"]["input_dir"]
	output_dir = config["do_stack"]["output_dir"]
	object_list = []

	if os.path.isfile(output_dir + "/stack.fit"):

		print("<STATUS> Stack already exists. Reading pre-existing stack ...")
		master_dark = fits.open(output_dir + "/stack.fit")

	else:

		os.chdir(input_dir)
		print("<STATUS> Changing to", input_dir, "as current working directory ...")

		for frame in glob.glob("*.fit"):

			print("<STATUS> Adding", frame, "to stack list ...")
			object_list.append(frame)

		print("<STATUS> Running [do_stack] ...")
		stack = do_stack(object_list, input_dir, output_dir)

	end = time.time()
	time = end - start
	print()
	print("%.2f" % time, "seconds to complete.")