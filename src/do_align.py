# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CAL

The function [do_wcs_align] aligns a series of FITS frames to a reference frame via WCS REPROJECT

Args:
	object_list <class 'list'> : list of FITS file names (each name is <class 'str'>)
	output_dir <class 'str'> : path to directory for saving aligned FITS files

Returns:
	n/a

---

The function [do_astro_align] aligns a series of FITS frames to a reference frame via ASTROALIGN

Args:
	object_list <class 'list'> : list of FITS file names (each name is <class 'str'>)
	output_dir <class 'str'> : path to directory for saving aligned FITS files

Returns:
	n/a

Date: 27 Apr 2019
Last update: 17 Jul 2019
"""

__author__ = "Richard Camuccio"
__version__ = "1.2.0"

from astropy import units as u
from astropy.io import fits
from astropy.wcs import WCS
from do_read import *
from reproject import reproject_interp
import astroalign as aa
import configparser
import glob
import math
import numpy as np
import os
import time

def do_wcs_align(object_list, output_dir):
	"""Align a series of frames to a reference frame via WCS"""

	if len(object_list) == 0:
		print(" [CAL][do_align][do_wcs_align]: Align list has zero objects... skipping align")

	else:
		print(" [CAL][do_align][do_wcs_align]: Opening reference frame", object_list[0])
		ref_fits = fits.open(object_list[0])

		print(" [CAL][do_align][do_wcs_align]: Reading reference frame data")
		ref_data = ref_fits[0].data

		print(" [CAL][do_align][do_wcs_align]: Running [do_read]")
		ref_hdr = do_read(object_list[0], output_dir)
		print(" [CAL][do_align][do_wcs_align]: Ending [do_read]")

		print(" [CAL][do_align][do_wcs_align]: Converting reference data to FITS")
		ref_hdu = fits.PrimaryHDU(ref_data, header=ref_hdr)

		print(" [CAL][do_align][do_wcs_align]: Writing reference frame to", output_dir)
		ref_hdu.writeto(output_dir + "/a-" + str(object_list[0]))

		for i in range(1, len(object_list)):

			print(" [CAL][do_align][do_wcs_align]: Opening target frame", object_list[i])
			tar_fits = fits.open(object_list[i])

			print(" [CAL][do_align][do_wcs_align]: Reading target frame data")
			tar_data = tar_fits[0].data

			print()
			print(" [CAL][do_align][do_wcs_align]: Running [do_read]")
			tar_hdr = do_read(object_list[i], output_dir)
			print(" [CAL][do_align][do_wcs_align]: Ending [do_read]")
			print()

			print(" [CAL][do_align][do_wcs_align]: Converting target data to FITS")
			tar_hdu = fits.PrimaryHDU(tar_data, header=tar_hdr)

			print(" [CAL][do_align][do_wcs_align]: Aligning target frame with reference frame")
			array, footprint = reproject_interp(tar_hdu, ref_hdr)

			print(" [CAL][do_align][do_wcs_align]: Converting aligned data to FITS")
			tar_hdu = fits.PrimaryHDU(array, header=tar_hdr)

			print(" [CAL]: Writing aligned frame to", output_dir)
			tar_hdu.writeto(output_dir + "/a-" + str(object_list[i]))

	return

def do_astro_align(object_list, output_dir):
	"""Align a series of frames to a reference frame via ASTROALIGN"""

	if len(object_list) == 0:
		print(" [CAL][do_align][do_astro_align]: Align list has zero objects... skipping align")

	else:
		print(" [CAL][do_align][do_astro_align]: Opening reference frame", object_list[0])
		ref_fits = fits.open(object_list[0])

		print(" [CAL][do_align][do_astro_align]: Reading reference frame data")
		ref_data = ref_fits[0].data

		print(" [CAL][do_align][do_astro_align]: Running [do_read]")
		ref_hdr = do_read(object_list[0], output_dir)
		print(" [CAL][do_align][do_astro_align]: Ending [do_read]")

		print(" [CAL][do_align][do_astro_align]: Converting reference data to FITS")
		ref_hdu = fits.PrimaryHDU(ref_data, header=ref_hdr)

		print(" [CAL][do_align][do_astro_align]: Writing reference frame to", output_dir)
		ref_hdu.writeto(output_dir + "/a-" + str(object_list[0]))

		for i in range(1, len(object_list)):

			print(" [CAL][do_align][do_astro_align]: Opening target frame", object_list[i])
			tar_fits = fits.open(object_list[i])

			print(" [CAL][do_align][do_astro_align]: Reading target frame data")
			tar_data = tar_fits[0].data

			print()
			print(" [CAL][do_align][do_astro_align]: Running [do_read]")
			tar_hdr = do_read(object_list[i], output_dir)
			print(" [CAL][do_align][do_astro_align]: Ending [do_read]")
			print()

			print(" [CAL][do_align][do_astro_align]: Aligning target", object_list[i], "with reference", object_list[0])
			array = aa.register(target_data, reference_data)

			print(" [CAL][do_align][do_astro_align]: Converting frame aligned data to FITS")
			tar_hdu = fits.PrimaryHDU(array, header=tar_hdr)

			print(" [CAL][do_align][do_astro_align]: Saving aligned frame to directory", output_dir)
			tar_hdu.writeto(output_dir + "/a-" + str(object_list[i]))

	return

if __name__ == "__main__":

	os.system("clear")

	print(" Running CAL")
	print()
	print(" [CAL]: Running [do_align] as script")
	start = time.time()

	print(" [CAL]: Reading configuration file")
	config = configparser.ConfigParser()
	config.read("/home/rcamuccio/Documents/CAL/config/config.ini")

	print(" [CAL]: Parsing directory paths")
	input_dir = config["do_align"]["input_dir"]
	output_dir = config["do_align"]["output_dir"]

	print(" [CAL]: Checking if output path exists")
	if not os.path.exists(output_dir):
		print(" [CAL]: Creating output directory", output_dir)
		os.makedirs(output_dir)
	
	print(" [CAL]: Changing to", input_dir, "as current working directory")
	os.chdir(input_dir)

	object_list = []

	for frame in glob.glob("*.fit"):

		if os.path.isfile(str(output_dir) + "/a-" + str(frame)):
			print(" [CAL]: Aligned frame of", frame, "already exists")
			print(" [CAL]: Skipping align on frame", frame)

		else:
			print(" [CAL]: Adding", frame, "to align list")
			object_list.append(frame)

	print(" [CAL]: Sorting align list")
	object_list = sorted(object_list)

	if config["do_align"]["wcs_align"] == "yes":

		print()
		print(" [CAL]: Running [do_align][do_wcs_align]")
		print()

		do_wcs_align(object_list, output_dir)

		print()
		print(" [CAL]: Ending [do_align][do_wcs_align]")
		print()

	elif config["do_align"]["wcs_align"] == "no":

		print()
		print(" [CAL]: Running [do_align][do_astro_align]")
		print()

		do_astro_align(object_list, output_dir)

		print()
		print(" [CAL]: Ending [do_align][do_astro_align]")
		print()

	end = time.time()
	time = end - start
	print(" End of script.", "%.2f" % time, "seconds to complete.")