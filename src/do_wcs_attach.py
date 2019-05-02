# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Richard Camuccio
# 2 May 2019
#
# Last update: 2 May 2019
#
# Function: do_wcs_attach (CAL)
#

from astropy.io import fits
import configparser
import glob
import os
import subprocess
import time

print("<STATUS> Reading configuration file ...")
config = configparser.ConfigParser()
config.read("/home/rcamuccio/Documents/CAL/config.ini")

def do_wcs_attach(object_list, input_dir, output_dir):
	"""Create WCS-attached FITS to series of frames using Astrometry.net"""

	for item in object_list:

		file = item[:-4]
		
		file_axy = file + ".axy"
		file_corr = file + ".corr"
		file_match = file + ".match"
		file_new = file + ".new"
		file_rdls = file + ".rdls"
		file_solved = file + ".solved"
		file_wcs = file + ".wcs"
		file_xyls = file + "-indx.xyls"

		print("<STATUS> Initiating astrometry.net code on", item, "...")
		subprocess.run(["solve-field", "--no-plots", item])

		print("<STATUS> Cleaning up ...")
		subprocess.run(["rm", file_axy])
		subprocess.run(["rm", file_corr])
		subprocess.run(["rm", file_match])
		subprocess.run(["rm", file_rdls])
		subprocess.run(["rm", file_solved])
		subprocess.run(["rm", file_wcs])
		subprocess.run(["rm", file_xyls])

		print("<STATUS> Moving solved fields to output directory", output_dir)
		print(file_new)
		print(output_dir + str("/wcs-") + file + ".fit")
		subprocess.run(["mv", file_new, output_dir + str("/wcs-") + file + ".fit"])

	return

if __name__ == "__main__":

	start = time.time()

	input_dir = config["do_wcs_attach"]["input_dir"]
	output_dir = config["do_wcs_attach"]["output_dir"]
	object_list = []

	if not os.path.exists(output_dir):

		os.makedirs(output_dir)

	os.chdir(input_dir)
	print("<STATUS> Changing to", input_dir, "as current working directory ...")

	for frame in glob.glob("*.fit"):

		print("<STATUS> Adding", frame, "to align list ...")
		object_list.append(frame)

	print("<STATUS> Running [do_wcs_attach] ...")
	do_wcs_attach(object_list, input_dir, output_dir)

	end = time.time()
	time = end - start
	print()
	print("%.2f" % time, "seconds to complete.")