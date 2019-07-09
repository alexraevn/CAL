# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CAL

The function [do_read] reads a FITS frame and returns an updated FITS header

Args:
	frame <class 'str'> : FITS file name
	output_dir <class 'str'> : path for saving log

Returns:
	hdr <class 'astropy.io.fits.header.Header'> : Updated FITS header

Date: 27 Apr 2019
Last update: 6 Jul 2019
"""

__author__ = "Richard Camuccio"
__version__ = "1.1.0"

from astropy.io import fits
import configparser
import glob
import os
import time

def do_read(frame, output_dir):

	print(" [CAL][do_read]: Opening log")
	log = open(output_dir + "/log.txt", "a")

	config = configparser.ConfigParser()
	config.read("/home/rcamuccio/Documents/CAL//config/obs.ini")

	print(" [CAL][do_read]: Opening frame", frame)
	fits_frame = fits.open(frame, mode="update")
	log.write("Frame: " + str(frame) + "\n")

	print(" [CAL][do_read]: Reading header")
	hdr = fits_frame[0].header

	# Read header value for 'aperture area' keyword (in mm^2)
	try:
		hdr_aptarea = fits_frame[0].header["APTAREA"]

		if hdr_aptarea == 0.0:
			hdr["APTAREA"] = config["telescope"]["aperture_area"]

		log.write("  APTAREA = " + str(hdr["APTAREA"]) + " mm^2\n")

	except KeyError:
		hdr["APTAREA"] = config["telescope"]["aperture_area"]

		log.write("  APTAREA = " + str(hdr["APTAREA"]) + " mm^2\n")

	# Read header value for 'aperature diameter' keyword (in mm)
	try:
		hdr_aptdia = fits_frame[0].header["APTDIA"]

		if hdr_aptdia == 0.0:
			hdr["APTDIA"] = config["telescope"]["aperture_diameter"]

		log.write("  APTDIA = " + str(hdr["APTDIA"]) + " mm\n")

	except KeyError:
		hdr["APTDIA"] = config["telescope"]["aperture_diameter"]

		log.write("  APTDIA = " + str(hdr["APTDIA"]) + " mm\n")

	# Read header value for 'CCD temperature' keyword (in deg C)
	try:
		hdr_ccdtemp = fits_frame[0].header["CCD-TEMP"]

		log.write("  CCD-TEMP = " + str(hdr["CCD-TEMP"]) + " C\n")

	except KeyError:
		log.write("  CCD-TEMP = none\n")

	# Read header value for 'observation date' keyword
	try:
		hdr_dateobs = fits_frame[0].header["DATE-OBS"]

		log.write("  DATE-OBS = " + str(hdr["DATE-OBS"]) + "\n")

	except KeyError:
		log.write("  DATE-OBS = none\n")

	# Read header value for 'exposure time' keyword (in s)
	try:
		hdr_exptime = fits_frame[0].header["EXPTIME"]

		log.write("  EXPTIME = " + str(hdr["EXPTIME"]) + " s\n")

	except KeyError:
		log.write("  EXPTIME = none\n")

	# Read header value for 'filter' keyword
	try:
		hdr_filter = fits_frame[0].header["FILTER"]

		if hdr_filter == "":
			hdr["FILTER"] = "unfiltered"

		log.write("  FILTER = " + str(hdr["FILTER"]) + "\n")

	except KeyError:
		hdr["FILTER"] = "unfiltered"

		log.write("  FILTER = " + str(hdr["FILTER"]) + "\n")

	# Read header value for 'focal length' keyword (in mm)
	try:
		hdr_focallen = fits_frame[0].header["FOCALLEN"]

		if hdr_focallen == 0.0:
			hdr["FOCALLEN"] = config["telescope"]["focal_length"]

		log.write("  FOCALLEN = " + str(hdr["FOCALLEN"]) + " mm\n")

	except KeyError:
		hdr["FOCALLEN"] = config["telescope"]["focal_length"]

		log.write("  FOCALLEN = NONE\n")

	# Read header value for 'image type' keyword
	try:
		hdr_imagetype = fits_frame[0].header["IMAGETYP"]

		log.write("  IMAGETYP = " + str(hdr["IMAGETYP"]) + "\n")

	except KeyError:
		log.write("  IMAGETYP = none\n")

	# Read header value for 'instrument' keyword
	try:
		hdr_instrument = fits_frame[0].header["INSTRUME"]

		if hdr_instrument == "":
			hdr["INSTRUME"] = config["telescope"]["name"]

		log.write("  INSTRUME = " + str(hdr["INSTRUME"]) + "\n")

	except KeyError:
		hdr["INSTRUME"] = config["telescope"]["name"]

		log.write("  INSTRUME = none\n")

	# Read header value for 'Julian Date' keyword
	try:
		hdr_jd = fits_frame[0].header["JD"]

		log.write("  JD = " + str(hdr["JD"]) + "\n")

	except KeyError:
		log.write("  JD = none\n")

	# Read header value for 'Heliocentric Julian Date' keyword
	try:
		hdr_jdhelio = fits_frame[0].header["JD-HELIO"]

		log.write("  JD-HELIO = " + str(hdr["JD-HELIO"]) + "\n")

	except KeyError:
		log.write("  JD-HELIO = none\n")

	# Read header value for 'object' keyword
	try:
		hdr_object = fits_frame[0].header["OBJECT"]

		log.write("  OBJECT = " + str(hdr["OBJECT"]) + "\n")

	except KeyError:
		log.write("  OBJECT = none\n")

	# Read header value for 'observer' keyword
	try:
		hdr_observer = fits_frame[0].header["OBSERVER"]

		if hdr_observer == "":
			hdr["OBSERVER"] = config["main"]["observer"]

		log.write("  OBSERVER = " + str(hdr["OBSERVER"]) + "\n")

	except KeyError:
		hdr["OBSERVER"] = config["main"]["observer"]

		log.write("  OBSERVER = none\n")

	# Read header value for 'telescope' keyword
	try:
		hdr_telescope = fits_frame[0].header["TELESCOP"]

		if hdr_telescope == "":
			hdr["TELESCOP"] = config["main"]["name"]

		log.write("  TELESCOP = " + str(hdr["TELESCOP"]) + "\n")

	except KeyError:
		hdr["TELESCOP"] = config["main"]["name"]

		log.write("  TELESCOP = NONE\n")

	# Read header value for 'x binning' keyword
	try:
		hdr_xbinning = fits_frame[0].header["XBINNING"]

		log.write("  XBINNING = " + str(hdr["XBINNING"]) + "\n")

	except KeyError:
		log.write("  XBINNING = NONE\n")

	# Read header value for 'y binning' keyword
	try:
		hdr_ybinning = fits_frame[0].header["YBINNING"]

		log.write("  YBINNING = " + str(hdr["YBINNING"]) + "\n")

	except KeyError:
		log.write("  YBINNING = NONE\n")

		log.write("\n\n")

	log.close()

	return hdr

if __name__ == "__main__":

	os.system("clear")

	print(" [CAL]: Running CAL")
	print()
	print(" [CAL]: Running [do_read] as script")
	start = time.time()

	print(" [CAL]: Reading configuration file")
	config = configparser.ConfigParser()
	config.read("/home/rcamuccio/Documents/CAL//config/config.ini")

	print(" [CAL]: Parsing directory paths")
	input_dir = config["do_read"]["input_dir"]
	output_dir = config["do_read"]["output_dir"]

	print(" [CAL]: Changing to", input_dir, "as current working directory")
	os.chdir(input_dir)

	object_list = []

	for frame in glob.glob("*.fit"):
		print(" [CAL]: Adding", frame, "to read list ...")
		object_list.append(frame)

	print(" [CAL]: Sorting object list")
	object_list = sorted(object_list)

	for item in object_list:

		print()
		print(" [CAL]: Running [do_read]")
		print()

		do_read(item, output_dir)

		print()
		print(" [CAL]: Ending [do_read]")
		print()

	end = time.time()
	time = end - start
	print(" End of script.", "%.2f" % time, "seconds to complete.")