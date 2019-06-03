# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Richard Camuccio
# 3 Jun 2019
#
# Last update: 3 Jun 2019
#
# Function: do_cosmicray_detect (CAL)
#

from astropy import units as u
from astropy.io import fits
import astroscrappy
import configparser
import glob
import numpy as np
import os
import time

print("[CAL]: Reading configuration file ...")
config = configparser.ConfigParser()
config.read("/home/rcamuccio/Documents/CAL/config.ini")

def do_cosmicray_detect(object_list, input_dir, output_dir):
	"""Detect and remove cosmic rays from a series of object frames"""

	for item in object_list:

		if os.path.isfile(str(output_dir) + "/cal-" + str(item)):

			print("[CAL]: Skipping cosmic ray detection on frame", item, "...")

		else:

			print("[CAL]: Opening frame", item, "...")
			frame = fits.open(item)

			print("[CAL]: Reading frame", item, "data ...")
			frame_data = frame[0].data

			print("[CAL]: Detecting and removing cosmic rays ...")
			crmask, cleanarr = astroscrappy.detect_cosmics(frame_data, inmask=None, sigclip=4.0, satlevel=np.inf, sepmed=False, cleantype="medmask", fsmode="median")

			print("[CAL]: Converting cleaned array to FITS ...")
			clean_frame = fits.PrimaryHDU(cleanarr)

			if config["do_cosmicray_detect"]["write_cal"] == "yes":

				print("[CAL]: Saving FITS to directory", output_dir, "...")
				clean_frame.writeto(output_dir + "/cal-" + str(item), overwrite=True)

	return

if __name__ == "__main__":

	start = time.time()

	input_dir = config["do_cosmicray_detect"]["input_dir"]
	output_dir = config["do_cosmicray_detect"]["output_dir"]
	object_list = []

	if not os.path.exists(output_dir):
   		os.makedirs(output_dir)

	os.chdir(input_dir)
	print("[CAL]: Changing to", input_dir, "as current working directory ...")

	for frame in glob.glob("*.fit"):

		print("[CAL]: Adding", frame, "to detection list ...")
		object_list.append(frame)

	print("[CAL]: Running [do_cosmicray_detect] ...")
	do_cosmicray_detect(object_list, input_dir, output_dir)

	end = time.time()
	time = end - start
	print()
	print("[CAL]", "%.2f" % time, "seconds to complete.")