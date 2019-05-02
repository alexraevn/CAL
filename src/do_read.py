# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Richard Camuccio
# 27 Apr 2019
#
# Last update: 27 Apr 2019
#
# Function: do_read (CAL)
#

from astropy.io import fits

import configparser
import glob
import os
import time

print("<STATUS> Reading configuration file ...")
config = configparser.ConfigParser()
config.read("/home/rcamuccio/Documents/CAL/config.ini")

def do_read(object_list, input_dir, output_dir):

	log = open("log.txt", "w+")

	for item in object_list:

		frame = fits.open(item)

		date = frame[0].header["DATE-OBS"]
		exp_time = frame[0].header["EXPTIME"]
		ccd_temp = frame[0].header["CCD-TEMP"]
		binning = (frame[0].header["XBINNING"], frame[0].header["YBINNING"])
		img_type = frame[0].header["IMAGETYP"]
		color = frame[0].header["FILTER"]

		log.write("Frame: " + str(frame) + "\n")
		log.write("Date: " + str(date) + "\n")
		log.write("Exposure time: " + str(exp_time) + " s\n")
		log.write("CCD temperature: " + str(ccd_temp) + " C\n")
		log.write("Binning: " + str(binning) + "\n")
		log.write("Image type: " + str(img_type) + "\n")
		log.write("Filter: " + str(color) + "\n")
		log.write("\n")

	log.write("End of read")
	log.close()

	return

if __name__ == "__main__":

	start = time.time()

	input_dir = config["do_read"]["input_dir"]
	output_dir = config["do_read"]["output_dir"]
	object_list = []

	os.chdir(input_dir)
	print("<STATUS> Changing to", input_dir, "as current working directory ...")

	for frame in glob.glob("*.fit"):

		print("<STATUS> Adding", frame, "to read list ...")
		object_list.append(frame)

	print("<STATUS> Running [do_read] ...")
	do_read(object_list, input_dir, output_dir)

	end = time.time()
	time = end - start
	print()
	print("%.2f" % time, "seconds to complete.")