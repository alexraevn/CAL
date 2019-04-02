# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Richard Camuccio
# 14 May 2018
#
# Last update: 2 Apr 2019
#
# Transient optical follow-up pipeline
#

import cal
import ccdproc
import configparser
import errno
import glob
import os
import numpy as np
import shutil
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

#
# TARGET
#

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

# Calibrate object frames
for directory in tar_obj_dir:

	os.chdir(directory)
	print("<STATUS:TOFU> Changing to", directory, "as current working directory ...")

	# Create sub-directories within object directory
	raw_path = directory + "/raw"
	cal_path = directory + "/cal"
	align_path = directory + "/align"
	stack_path = directory + "/stack"

	path_list = [raw_path, cal_path, align_path, stack_path]

	for path in path_list:
		
		try:

			os.makedirs(path)
			print("<STATUS:TOFU> Creating new directory in", path, "...")

		except OSError as e:

			if e.errno == errno.EEXIST:
				print("<STATUS:TOFU>", path, "already exists! Skipping ...")

			else:
				raise

	# Create a list of object frames for calibration
	tar_obj_list = []

	for frame in glob.glob("*.fit"):

		if "a-" in frame:
			print("<STATUS:TOFU> Not adding frame", frame, "to calibration list ...")

			try:
				shutil.move(frame, align_path)
				print("<STATUS:TOFU> Moving", frame, "to", align_path, "...")

			except Exception as e:
				print("<STATUS:TOFU> Not moving", frame, "-- type error:", e, "...")

		elif "cal-" in frame:
			print("<STATUS:TOFU> Not adding frame", frame, "to calibration list ...")

			try:
				shutil.move(frame, cal_path)
				print("<STATUS:TOFU> Moving", frame, "to", cal_path, "...")

			except Exception as e:
				print("<STATUS:TOFU> Not moving", frame, "-- type error:", e, "...")

		elif "stack" in frame:
			print("<STATUS:TOFU> Not adding frame", frame, "to calibration list ...")

			try:
				shutil.move(frame, stack_path)
				print("<STATUS:TOFU> Moving", frame, "to", stack_path, "...")

			except Exception as e:
				print("<STATUS:TOFU> Not moving", frame, "-- type error:", e, "...")
			
		else:
			print("<STATUS:TOFU> Adding frame", frame, "to calibration list ...")
			tar_obj_list.append(frame)

	# Calibrate target frames
	print("<STATUS:TOFU> Starting calibration on frames", tar_obj_list, "...")
	cal.do_calibrate(tar_obj_list, tar_master_dark, tar_master_flat, cal_path)

	for frame in glob.glob("*.fit"):

		try:
			shutil.move(frame, raw_path)
			print("<STATUS:TOFU> Moving", frame, "to", raw_path, "...")

		except Exception as e:
			print("<STATUS:TOFU> Not moving", frame, "-- type error:", e, "...")

#
# REFERENCE
#

# Make master dark
directory = ref_dark_dir[0]

os.chdir(directory)
print("<STATUS:TOFU> Changing to", directory, "as current working directory ...")

ref_dark_list = []

if os.path.isfile("master-dark.fit"):

	print("<STATUS:TOFU> Reading master dark ...")
	ref_master_dark = ccdproc.fits_ccddata_reader("master-dark.fit")

else:

	for frame in glob.glob("*.fit"):

		print("<STATUS:TOFU> Adding", frame, "to dark combine list ...")
		ref_dark_list.append(frame)

	print("<STATUS:TOFU> Starting dark combine ...")
	ref_master_dark = cal.do_dark_master(ref_dark_list)

	print("<STATUS:TOFU> Saving master dark to directory", directory, "...")
	ccdproc.fits_ccddata_writer(ref_master_dark, str(directory) + "/master-dark.fit")

# Make master flat
directory = ref_flat_dir[0]

os.chdir(directory)
print("<STATUS:TOFU> Changing to", directory, "as current working directory ...")

ref_flat_list = []

if os.path.isfile("master-flat.fit"):

	print("<STATUS:TOFU> Reading master flat ...")
	ref_master_flat = ccdproc.fits_ccddata_reader("master-flat.fit")

else:

	for frame in glob.glob("*.fit"):

		print("<STATUS:TOFU> Adding frame", frame, "to flat combine list ...")
		ref_flat_list.append(frame)

	print("<STATUS:TOFU> Starting flat master ...")
	ref_master_flat = cal.do_flat_master(ref_flat_list, ref_master_dark)

	print("<STATUS:TOFU> Saving master flat to directory", directory, "...")
	ccdproc.fits_ccddata_writer(ref_master_flat, str(directory) + "/master-flat.fit")

# Calibrate object frames
for directory in ref_obj_dir:

	os.chdir(directory)
	print("<STATUS:TOFU> Changing to", directory, "as current working directory ...")

	# Create sub-directories within object directory
	raw_path = directory + "/raw"
	cal_path = directory + "/cal"
	align_path = directory + "/align"
	stack_path = directory + "/stack"

	path_list = [raw_path, cal_path, align_path, stack_path]

	for path in path_list:
		
		try:

			os.makedirs(path)
			print("<STATUS:TOFU> Creating new directory in", path, "...")

		except OSError as e:

			if e.errno == errno.EEXIST:
				print("<STATUS:TOFU>", path, "already exists! Skipping ...")

			else:
				raise

	# Create a list of object frames for calibration
	ref_obj_list = []

	for frame in glob.glob("*.fit"):

		if "a-" in frame:
			print("<STATUS:TOFU> Not adding frame", frame, "to calibration list ...")

			try:
				shutil.move(frame, align_path)
				print("<STATUS:TOFU> Moving", frame, "to", align_path, "...")

			except Exception as e:
				print("<STATUS:TOFU> Not moving", frame, "-- type error:", e, "...")

		elif "cal-" in frame:
			print("<STATUS:TOFU> Not adding frame", frame, "to calibration list ...")

			try:
				shutil.move(frame, cal_path)
				print("<STATUS:TOFU> Moving", frame, "to", cal_path, "...")

			except Exception as e:
				print("<STATUS:TOFU> Not moving", frame, "-- type error:", e, "...")

		elif "stack" in frame:
			print("<STATUS:TOFU> Not adding frame", frame, "to calibration list ...")

			try:
				shutil.move(frame, stack_path)
				print("<STATUS:TOFU> Moving", frame, "to", stack_path, "...")

			except Exception as e:
				print("<STATUS:TOFU> Not moving", frame, "-- type error:", e, "...")
			
		else:
			print("<STATUS:TOFU> Adding frame", frame, "to calibration list ...")
			ref_obj_list.append(frame)

	# Calibrate target frames
	print("<STATUS:TOFU> Starting calibration on frames", ref_obj_list, "...")
	cal.do_calibrate(ref_obj_list, ref_master_dark, ref_master_flat, cal_path)

	for frame in glob.glob("*.fit"):

		try:
			shutil.move(frame, raw_path)
			print("<STATUS:TOFU> Moving", frame, "to", raw_path, "...")

		except Exception as e:
			print("<STATUS:TOFU> Not moving", frame, "-- type error:", e, "...")

end = time.time()
print()
print(str(end - start) + " seconds to complete.")