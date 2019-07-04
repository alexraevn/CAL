# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CAL

The function [do_read] creates a master dark FITS file

Args:
	object_list <class 'list'> : list of FITS file names (each name is <class 'str'>)
	output_dir <class 'str'> : path to directory for saving read log

Returns:
	n/a

Date: 27 Apr 2019
Last update: 2 Jul 2019
"""

__author__ = "Richard Camuccio"
__version__ = "1.0"

from astropy.io import fits
import configparser
import glob
import os
import time

def do_read(object_list, output_dir):

	log = open("log.txt", "w+")

	for item in object_list:

		frame = fits.open(item)
		log.write("Frame: " + str(item) + "\n")

		try:
			img_type = frame[0].header["IMAGETYP"]
			log.write("Image type: " + str(img_type) + "\n")
		except KeyError:
			log.write("Image type: None \n")

		try:
			date = frame[0].header["DATE-OBS"]
			log.write("Date: " + str(date) + "\n")
		except KeyError:
			log.write("Date: None \n")

		try:
			exp_time = frame[0].header["EXPTIME"]
			log.write("Exposure time: " + str(exp_time) + " s\n")
		except KeyError:
			log.write("Exposure time: None \n")

		try:
			ccd_temp = frame[0].header["CCD-TEMP"]
			log.write("CCD temperature: " + str(ccd_temp) + " C\n")
		except KeyError:
			log.write("CCD temperature: None \n")

		try:
			binning = (frame[0].header["XBINNING"], frame[0].header["YBINNING"])
			log.write("Binning: " + str(binning) + "\n")
		except KeyError:
			log.write("Binning: None \n")

		try:
			color = frame[0].header["FILTER"]
			log.write("Filter: " + str(color) + "\n")
		except KeyError:
			log.write("Filter: None \n")

		log.write("\n")

	log.write("[CAL]: End of read")
	log.close()

	return

if __name__ == "__main__":

	start = time.time()

	print(" [CAL]: Reading configuration file ...")
	config = configparser.ConfigParser()
	config.read("/home/rcamuccio/Documents/CAL//config/config.ini")

	input_dir = config["do_read"]["input_dir"]
	output_dir = config["do_read"]["output_dir"]
	object_list = []

	os.chdir(input_dir)
	print(" [CAL]: Changing to", input_dir, "as current working directory ...")

	for frame in glob.glob("*.fit"):

		print(" [CAL]: Adding", frame, "to read list ...")
		object_list.append(frame)

	print(" [CAL]: Sorting object list ...")
	object_list = sorted(object_list)

	print(" [CAL]: Running [do_read] ...")
	do_read(object_list, output_dir)

	end = time.time()
	time = end - start
	print()
	print(" [CAL]: Script [do_read] completed in", "%.2f" % time, "s")