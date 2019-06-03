# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Richard Camuccio
# 3 Jun 2019
#
# Last update: 3 Jun 2019
#
# Function: do_frame_sub (CAL)
#

from astropy import units as u
from astropy.io import fits
import configparser
import glob
import numpy as np
import ois
import os
import time

print("[CAL]: Reading configuration file ...")
config = configparser.ConfigParser()
config.read("/home/rcamuccio/Documents/CAL/config.ini")

def do_frame_sub(reference_frame, target_frame, output_dir):
	"""Subtract a (later) target frame from an (earler) reference frame"""

	if os.path.isfile(str(output_dir) + "/subtract.fit"):

			print("[CAL]: Difference frame exists! Skipping subtraction ...")

	else:

		print("[CAL]: Opening reference", reference_frame, "frame ...")
		reference_frame = fits.open(reference_frame)

		print("[CAL]: Reading reference", reference_frame, "data ...")
		reference_data = reference_frame[0].data

		print("[CAL]: Opening target", target_frame, "frame ...")
		target_frame = fits.open(target_frame)

		print("[CAL]: Reading target", target_frame, "data ...")
		target_data = target_frame[0].data

		print("[CAL]: Subtracting target from reference ...")
		diff_image, optimal_image, kernel, background = ois.optimal_system(reference_data, target_data, kernelshape=(3,3), method="Bramich")

		print("[CAL]: Converting difference image array to FITS ...")
		diff_frame = fits.PrimaryHDU(diff_image)

		if config["do_frame_sub"]["write_diff"] == "yes":

			print("[CAL]: Saving FITS to directory", output_dir, "...")
			diff_frame.writeto(output_dir + "/subtract.fit", overwrite=True)

	return

if __name__ == "__main__":

	start = time.time()

	reference_frame = config["do_frame_sub"]["reference_frame"]
	target_frame = config["do_frame_sub"]["target_frame"]
	output_dir = config["do_frame_sub"]["output_dir"]

	if not os.path.exists(output_dir):

		print("[CAL]: Creating output directory", output_dir, "...")
		os.makedirs(output_dir)

	print("[CAL]: Running [do_frame_sub] ...")
	do_frame_sub(reference_frame, target_frame, output_dir)

	end = time.time()
	time = end - start
	print()
	print("[CAL]", "%.2f" % time, "seconds to complete.")