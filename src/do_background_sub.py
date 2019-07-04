# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CAL

The function [do_background_sub] measures and subtracted the background signal from a series of FITS frames

Args:
	object_list <class 'list'> : list of FITS file names (each name is <class 'str'>)
	output_dir <class 'str'> : path to directory for saving background-subtracted frames
	sub_method <class 'str'> : options are "mean" and "median"; default value is "median"

Returns:
	n/a

Date: 28 Apr 2019
Last update: 4 Jul 2019
"""

__author__ = "Richard Camuccio"
__version__ = "1.0"

from astropy import units as u
from astropy.io import fits
from astropy.stats import biweight_location
from astropy.stats import mad_std
from astropy.stats import SigmaClip
from astropy.stats import sigma_clipped_stats
from photutils import Background2D
from photutils import make_source_mask
from photutils import MedianBackground
import configparser
import glob
import numpy as np
import os
import time

def do_simple_bkgsub(object_list, output_dir, sub_method="median"):

	for item in object_list:

		print(" [CAL][do_simple_bkgsub]: Opening frame", item, "...")
		frame = fits.open(item)

		print(" [CAL][do_simple_bkgsub]: Reading frame", item, "data ...")
		frame_data = frame[0].data

		print(" [CAL][do_simple_bkgsub]: Calculating mean of", item, "...")
		mean = np.mean(frame_data)

		print(" [CAL][do_simple_bkgsub]: Calculating median of", item, "...")
		median = np.median(frame_data)

		print(" [CAL][do_simple_bkgsub]: Calculating biweight location of", item, "...")
		bw_loc = biweight_location(frame_data)

		print(" [CAL][do_simple_bkgsub]: Calculating mean absolute deviation of", item, "...")
		mean_abs_dev = mad_std(frame_data)

		print(" ---------------------------------------------")
		print("  Simple statistics for", item)
		print("   Mean:", "%.3f" % mean, "ADU")
		print("   Median:", "%.3f" % median, "ADU")
		print("   Biweight location:", "%.3f" % bw_loc, "ADU")
		print("   Mean absolute deviation:", "%.3f" % mean_abs_dev, "ADU")
		print(" ---------------------------------------------")

		if sub_method == "median":
			print(" [CAL][do_simple_bkgsub]: Subtracting median from array ...")
			bkgsub_data = frame_data - median

		elif sub_method == "mean":
			print(" [CAL][do_simple_bkgsub]: Subtracting mean from array ...")
			bkgsub_data = frame_data - mean

		print(" [CAL][do_simple_bkgsub]: Converting background-subtracted array to FITS ...")
		bkgsub_frame = fits.PrimaryHDU(bkgsub_data)

		print(" [CAL][do_simple_bkgsub]: Saving FITS to directory", output_dir, "...")
		bkgsub_frame.writeto(output_dir + "/simple-bkgsub-" + str(item), overwrite=True)

	return

def do_sigma_bkgsub(object_list, output_dir, sub_method="median", sigma=5.0):

	for item in object_list:

		print(" [CAL][do_sigma_bkgsub]: Opening frame", item, "...")
		frame = fits.open(item)

		print(" [CAL][do_sigma_bkgsub]: Reading frame", item, "data ...")
		frame_data = frame[0].data

		print(" [CAL][do_sigma_bkgsub]: Calculating statistics of", item, "...")
		mean, median, std = sigma_clipped_stats(frame_data, sigma=sigma)
									
		print(" ---------------------------------------------")
		print("  Sigma-clipped statistics for", item)
		print("   Sigma:", sigma)
		print("   Mean:", "%.3f" % mean, "ADU")
		print("   Median:", "%.3f" % median, "ADU")
		print("   Standard deviation:", "%.3f" % std, "ADU")
		print(" ---------------------------------------------")

		if sub_method == "median":
			print(" [CAL][do_sigma_bkgsub]: Subtracting median from array ...")
			bkgsub_data = frame_data - median
			
		elif sub_method == "mean":
			print(" [CAL][do_sigma_bkgsub]: Subtracting mean from array ...")
			bkgsub_data = frame_data - mean

		print(" [CAL][do_sigma_bkgsub]: Converting background-subtracted array to FITS ...")
		bkgsub_frame = fits.PrimaryHDU(bkgsub_data)

		print(" [CAL][do_sigma_bkgsub]: Saving FITS to directory", output_dir, "...")
		bkgsub_frame.writeto(output_dir + "/sigma-bkgsub-" + str(item), overwrite=True)

	return

def do_mask_bkgsub(object_list, output_dir, sub_method="median", sigma=3.0):

	for item in object_list:

		print(" [CAL][do_mask_bkgsub]: Opening frame", item, "...")
		frame = fits.open(item)

		print(" [CAL][do_mask_bkgsub]: Reading frame", item, "data ...")
		frame_data = frame[0].data

		print(" [CAL][do_mask_bkgsub]: Making source mask ...")
		mask = make_source_mask(frame_data, snr=2, npixels=5, dilate_size=50)

		print(" [CAL][do_mask_bkgsub]: Calculating statistics of", item, "...")
		mean, median, std = sigma_clipped_stats(frame_data, sigma=sigma, mask=mask)

		print(" ---------------------------------------------")
		print("  Source-masked statistics for", item)
		print("   Sigma:", sigma)
		print("   Mean:", "%.3f" % mean, "ADU")
		print("   Median:", "%.3f" % median, "ADU")
		print("   Standard deviation:", "%.3f" % std, "ADU")
		print(" ---------------------------------------------")

		print(" [CAL][do_mask_bkgsub]: Subtracting median from array ...")
		bkgsub_data = frame_data - median

		print(" [CAL][do_mask_bkgsub]: Converting background-subtracted array to FITS ...")
		bkgsub_frame = fits.PrimaryHDU(bkgsub_data)

		print(" [CAL][do_mask_bkgsub]: Saving FITS to directory", output_dir, "...")
		bkgsub_frame.writeto(output_dir + "/mask-bkgsub-" + str(item), overwrite=True)

	return

#def do_2d_bkgsub(object_list, output_dir, sub_method="median"):

	#for item in object_list:

		#print("<STATUS> Opening frame", item, "...")
		#frame = fits.open(item)

		#print("<STATUS> Reading frame", item, "data ...")
		#frame_data = frame[0].data

		#sigma_clip = SigmaClip(sigma=5.0)
		#bkg_estimator = MedianBackground()
		#bkg = Background2D(frame_data, (50, 50), filter_size=(3, 3), sigma_clip=sigma_clip, bkg_estimator=bkg_estimator)

		#print()
		#print("     Frame:", item)
		#print("     Sigma: 5.0")
		#print("     Median:", "%.3f" % bkg.background_median)
		#print("     RMS:", "%.3f" % bkg.background_rms_median)
		#print()

		#print("<STATUS> Subtracting background from array ...")
		#bkgsub_data = frame_data - bkg.background

		#print("<STATUS> Converting background-subtracted array to FITS ...")
		#bkgsub_frame = fits.PrimaryHDU(bkgsub_data)

		#print("<STATUS> Saving FITS to directory", output_dir, "...")
		#bkgsub_frame.writeto(output_dir + "/2d-bkgsub-" + str(item), overwrite=True)
	
	#return

if __name__ == "__main__":

	os.system("clear")

	print(" Running CAL ...")
	print()
	print(" [CAL]: Running [do_background_sub] as script ...")
	start = time.time()

	print(" [CAL]: Reading configuration file ...")
	config = configparser.ConfigParser()
	config.read("/home/rcamuccio/Documents/CAL/config/config.ini")

	print(" [CAL]: Parsing directory paths ...")
	input_dir = config["do_background_sub"]["input_dir"]
	output_dir = config["do_background_sub"]["output_dir"]

	print(" [CAL]: Checking if output path exists ...")
	if not os.path.exists(output_dir):
		print(" [CAL]: Creating output directory", output_dir, "...")
		os.makedirs(output_dir)

	print(" [CAL]: Changing to", input_dir, "as current working directory ...")
	os.chdir(input_dir)

	object_list = []

	for frame in glob.glob("*.fit"):

		print(" [CAL]: Adding", frame, "to calibration list ...")
		object_list.append(frame)

	print(" [CAL]: Sorting list ...")
	object_list = sorted(object_list)
	print(" [CAL]: Sorted list:", object_list, "...")

	print()
	print(" [CAL]: Running [do_background_sub][do_simple_bkgsub] ...")
	print()

	do_simple_bkgsub(object_list, output_dir)

	print()
	print(" [CAL]: Ending [do_background_sub][do_simple_bkgsub] ...")
	print()

	print(" [CAL]: Running [do_background_sub][do_sigma_bkgsub] ...")
	print()
	do_sigma_bkgsub(object_list, output_dir)
	
	print()
	print(" [CAL]: Ending [do_background_sub][do_sigma_bkgsub] ...")
	print()

	print(" [CAL]: Running [do_background_sub][do_mask_bkgsub] ...")
	print()

	do_mask_bkgsub(object_list, output_dir)

	print()
	print(" [CAL]: Ending [do_background_sub][do_mask_bkgsub] ...")
	print()

	end = time.time()
	time = end - start
	print(" End of script.", "%.2f" % time, "seconds to complete.")