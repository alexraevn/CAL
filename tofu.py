# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Richard Camuccio
# 14 May 2018
#
# Last update: 1 Apr 2019
#
# Transient optical follow-up pipeline
#

import cal
import ccdproc
import configparser
import glob
import os
import numpy as np
import time

start = time.time()

print("<STATUS:TOFU> Reading configuration file ...")
config = configparser.ConfigParser()
config.read("config.ini")

# Define input directory
input_dir = config["main"]["input_dir"]
print("<STATUS:TOFU> Input directory:", input_dir)

# Define directories
print("<STATUS:TOFU> Completing a directory navigation ...")
tar_obj_dir, tar_dark_dir, tar_flat_dir, ref_obj_dir, ref_dark_dir, ref_flat_dir = cal.do_tofu_nav(input_dir)

# Make master dark
directory = tar_dark_dir[0]

os.chdir(directory)
print("<STATUS:TOFU> Changing to", directory, "as current working directory ...")

tar_dark_list = []

if os.path.isfile("master-dark.fit"):

	print("<STATUS:TOFU> Reading master dark ...")
	tar_master_dark = ccdproc.fits_ccddata_reader("master-dark.fit")

else:

	for frame in glob.glob("*.fit"):

		print("<STATUS:TOFU> Adding", frame, "to dark combine list ...")
		tar_dark_list.append(frame)

	print("<STATUS:TOFU> Starting dark combine ...")
	tar_master_dark = cal.do_dark_master(tar_dark_list)

	print("<STATUS:TOFU> Saving master dark to directory", directory, "...")
	ccdproc.fits_ccddata_writer(tar_master_dark, str(directory) + "/master-dark.fit")

# Make master flat
directory = tar_flat_dir[0]

os.chdir(directory)
print("<STATUS:TOFU> Changing to", directory, "as current working directory ...")

tar_flat_list = []

if os.path.isfile("master-flat.fit"):

	print("<STATUS:TOFU> Reading master flat ...")
	tar_master_flat = ccdproc.fits_ccddata_reader("master-flat.fit")

else:

	for frame in glob.glob("*.fit"):

		print("<STATUS:TOFU> Adding frame", frame, "to flat combine list ...")
		tar_flat_list.append(frame)

	print("<STATUS:TOFU> Starting flat master ...")
	tar_master_flat = cal.do_flat_master(tar_flat_list, tar_master_dark)

	print("<STATUS:TOFU> Saving master flat to directory", directory, "...")
	ccdproc.fits_ccddata_writer(tar_master_flat, str(directory) + "/master-flat.fit")

end = time.time()
print()
print(str(end - start) + " seconds to complete.")