# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Richard Camuccio
# 26 Apr 2019
#
# Last update: 27 Apr 2019
#
# Function: do_flat_master (CAL)
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

def do_flat_master(flat_list, master_dark, dark_dir, flat_dir, output_dir):
	"""Create a normalized flatfield frame"""

	print("<STATUS> Combining flats ...")

	if config["main"]["flat_combine"] == "median":
		combined_flat = ccdproc.combine(flat_list, method="median", unit="adu")

	elif config["main"]["flat_combine"] == "mean":
		combined_flat = ccdproc.combine(flat_list, method="mean", unit="adu")

	print("<STATUS> Subtracting dark from combined flat ...")
	master_flat = ccdproc.subtract_dark(combined_flat, master_dark, data_exposure=combined_flat.header["exposure"]*u.second, dark_exposure=master_dark.header["exposure"]*u.second, scale=True)

	print("<STATUS> Reading master flat data ...")
	master_flat_data = np.asarray(master_flat)

	print("<STATUS> Normalizing master flat ... ")

	if config["main"]["flat_normalization"] == "median":
		flatfield_data = master_flat_data / np.median(master_flat_data)

	elif config["main"]["flat_normalization"] == "mean":
		flatfield_data = master_flat_data / np.mean(master_flat_data)

	print("<STATUS> Converting flatfield data to CCDData ...")
	flatfield = ccdproc.CCDData(flatfield_data, unit="adu")

	if config["main"]["write_flat"] == "yes":

		print("<STATUS> Writing flatfield to output directory ...")
		ccdproc.fits_ccddata_writer(flatfield, output_dir + "/flatfield.fit")

	elif config["main"]["write_flat"] == "no":
		pass

	return flatfield

if __name__ == "__main__":

	start = time.time()

	dark_dir = "/home/rcamuccio/Documents/CAL/data/test_do_flat_master"
	flat_dir = "/home/rcamuccio/Documents/CAL/data/test_do_flat_master"
	output_dir = "/home/rcamuccio/Documents/CAL/data/test_do_flat_master"
	flat_list = []

	if os.path.isfile(output_dir + "/flatfield.fit"):

		print("<STATUS> Reading pre-existing flatfield FITS ...")
		flatfield = fits.open(flat_dir + "/flatfield.fit")

	else:

		print("<STATUS> Opening master dark FITS ...")
		master_dark = ccdproc.fits_ccddata_reader(dark_dir + "/master-dark.fit")

		os.chdir(flat_dir)
		print("<STATUS> Changing to", flat_dir, "as current working directory ...")

		for frame in glob.glob("*.fit"):

			print("<STATUS> Adding", frame, "to flat combine list ...")
			flat_list.append(frame)

		print("<STATUS> Running `do_flat_master` ...")
		flatfield = do_flat_master(flat_list, master_dark, dark_dir, flat_dir, output_dir)

	end = time.time()
	print(str(end - start) + " seconds to complete.")