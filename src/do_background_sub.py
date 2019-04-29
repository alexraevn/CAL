# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Richard Camuccio
# 28 Apr 2019
#
# Last update: 28 Apr 2019
#
# Function: do_background_sub (CAL)
#

from astropy import units as u
from astropy.io import fits
from astropy.stats import biweight_location
from astropy.stats import mad_std
from astropy.stats import sigma_clipped_stats
from photutils import make_source_mask
import configparser
import glob
import numpy as np
import os
import time

print("<STATUS> Reading configuration file ...")
config = configparser.ConfigParser()
config.read("/home/rcamuccio/Documents/CAL/config.ini")

def do_background_sub(object_list, input_dir, output_dir):

	if config["do_background_sub"]["method"] == "simple":

		for item in object_list:

			print("<STATUS> Opening frame", item, "...")
			frame = fits.open(item)

			print("<STATUS> Reading frame", item, "data ...")
			frame_data = frame[0].data

			print("<STATUS> Calculating median of", item, "...")
			median = np.median(frame_data)

			print("<STATUS> Calculating biweight location of", item, "...")
			bw_loc = biweight_location(frame_data)

			print("<STATUS> Calculating mean absolute deviation of", item, "...")
			mean_abs_dev = mad_std(frame_data)

			print("<STATUS> Subtracting median from array ...")
			bkgsub_data = frame_data - median

			print("<STATUS> Converting background-subtracted array to FITS ...")
			bkgsub_frame = fits.PrimaryHDU(bkgsub_data)

			print("<STATUS> Saving FITS to directory", output_dir, "...")
			bkgsub_frame.writeto(output_dir + "/simple-bkgsub-" + str(item), overwrite=True)

	elif config["do_background_sub"]["method"] == "sigma":

		for item in object_list:

			print("<STATUS> Opening frame", item, "...")
			frame = fits.open(item)

			print("<STATUS> Reading frame", item, "data ...")
			frame_data = frame[0].data

			mean, median, std = sigma_clipped_stats(frame_data, sigma=3.0)

			print()
			print("Sigma-clipped background statistics for", item)
			print("Mean:", mean, "ADU")
			print("Median:", median, "ADU")
			print("STDEV:", std, "ADU")
			print()

	elif config["do_background_sub"]["method"] == "mask":

		for item in object_list:

			print("<STATUS> Opening frame", item, "...")
			frame = fits.open(item)

			print("<STATUS> Reading frame", item, "data ...")
			frame_data = frame[0].data

			mask = make_source_mask(frame_data, snr=2, npixels=20, dilate_size=100)
			mean, median, std = sigma_clipped_stats(frame_data, sigma=3.0, mask=mask)

			print()
			print("Source-masked background statistics for", item)
			print("Mean:", mean, "ADU")
			print("Median:", median, "ADU")
			print("STDEV:", std, "ADU")
			print()

	else:

		print("void")

	return

if __name__ == "__main__":

	start = time.time()

	input_dir = config["do_background_sub"]["input_dir"]
	output_dir = config["do_background_sub"]["output_dir"]
	object_list = []

	if not os.path.exists(output_dir):
   		os.makedirs(output_dir)

	os.chdir(input_dir)
	print("<STATUS> Changing to", input_dir, "as current working directory ...")

	for frame in glob.glob("*.fit"):

		print("<STATUS> Adding", frame, "to calibration list ...")
		object_list.append(frame)

	print("<STATUS> Running [do_background_sub] ...")
	do_background_sub(object_list, input_dir, output_dir)

	end = time.time()
	print(str(end - start) + " seconds to complete.")