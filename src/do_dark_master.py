# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Richard Camuccio
# 27 Apr 2019
#
# Last update: 27 Apr 2019
#
# Function: do_dark_master (CAL)
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

def do_dark_master(dark_list, input_dir, output_dir):
	"""Create a master dark frame"""

	print("<STATUS> Combining darks ...")

	if config["do_dark_master"]["dark_combine"] == "median":
		master_dark = ccdproc.combine(dark_list, method="median", unit="adu")

	elif config["do_dark_master"]["dark_combine"] == "mean":
		master_dark = ccdproc.combine(dark_list, method="mean", unit="adu")

	if config["do_dark_master"]["write_dark"] == "yes":

		print("<STATUS> Writing master dark to output directory ...")
		ccdproc.fits_ccddata_writer(master_dark, output_dir + "/master-dark.fit")

	elif config["do_dark_master"]["write_dark"] == "no":
		pass

	return master_dark

if __name__ == "__main__":

	start = time.time()

	input_dir = config["do_dark_master"]["input_dir"]
	output_dir = config["do_dark_master"]["output_dir"]
	dark_list = []

	if os.path.isfile(output_dir + "/master-dark.fit"):

		print("<STATUS> Reading pre-existing master dark FITS ...")
		master_dark = fits.open(output_dir + "/master-dark.fit")

	else:

		os.chdir(input_dir)
		print("<STATUS> Changing to", input_dir, "as current working directory ...")

		for frame in glob.glob("*.fit"):

			print("<STATUS> Adding", frame, "to dark combine list ...")
			dark_list.append(frame)

		print("<STATUS> Running [do_dark_master] ...")
		master_dark = do_dark_master(dark_list, input_dir, output_dir)

	end = time.time()
	print(str(end - start) + " seconds to complete.")