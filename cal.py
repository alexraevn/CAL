# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CTMO Analysis Library

Date: 7 Jun 2019
Last update: 4 Jul 2020

"""

__author__ = "Richard Camuccio"
__version__ = "2.0.0"

import astroalign as aa 
import astroscrappy
import ccdproc
import configparser
import glob
import numpy as np 
import os
import sep
import subprocess
import time
from astropy import units as u
from astropy.io import fits 
from astropy.stats import sigma_clipped_stats
from astropy.wcs import WCS
from photutils import make_source_mask
from reproject import reproject_interp

class Pipeline:

	def __init__(self):

		self.__name = "cal_pipeline"

	def __str__(self):

		return self.__name

	def get_name(self):

		return self.__name

	def align(self, object_list, output_dir, method):
		"""Align a series of frames to a reference frame via ASTROALIGN or WCS REPROJECTION"""

		if len(object_list) == 0 or len(object_list) == 1:
			print("Insufficient number of images for alignment")

		else:
			print("Opening reference frame")
			reference_frame = fits.open(object_list[0])
			reference_data = reference_frame[0].data
			reference_header = reference_frame[0].header

			print("Converting reference data to FITS")
			reference_hdu = fits.PrimaryHDU(reference_data, header=reference_header)

			print("Writing reference frame to output directory")
			reference_hdu.writeto(output_dir + "/a-" + str(object_list[0]), overwrite=True)

			for i in range(1, len(object_list)):

				print("Opening target frame", object_list[i])
				target_frame = fits.open(object_list[i])
				target_data = target_frame[0].data
				target_header = target_frame[0].header

				if method == "astroalign":

					print("Aligning target frame with reference frame via ASTROALIGN")
					array = aa.register(target_data, reference_data)

				elif method == "reproject":

					print("Converting target data to FITS")
					target_hdu = fits.PrimaryHDU(target_data, header=target_header)

					print("Aligning target frame with reference frame via WCS")
					array, footprint = reproject_interp(target_hdu, reference_header)

				print("Converting aligned target data to FITS")
				target_hdu = fits.PrimaryHDU(array, header=target_header)

				print("Writing aligned frame to output directory")
				target_hdu.writeto(output_dir + "/a-" + str(object_list[i]), overwrite=True)

		return

	def combine_darks(self, dark_dir, method="median"):

		os.chdir(dark_dir)
		dark_list = []

		for item in glob.glob("*.fit"):
			print("Adding", item, "to dark list")
			dark_list.append(item)

		if method == "median":
			print("Combining darks by median")
			master_dark = ccdproc.combine(dark_list, method="median", unit="adu", mem_limit=6e9)

		elif method == "mean":
			print("Combining darks by mean")
			master_dark = ccdproc.combine(dark_list, method="mean", unit="adu", mem_limit=6e9)

		else:
			print("Combining darks by median")
			master_dark = ccdproc.combine(dark_list, method="median", unit="adu", mem_limit=6e9)

		return master_dark

	def combine_flats(self, flat_dir, dark_dir, method="median"):

		os.chdir(flat_dir)
		flat_list = []

		for item in glob.glob("*.fit"):
			print("Adding", item, "to flat list")
			flat_list.append(item)

		if method == "median":
			print("Combining flats by median")
			combined_flat = ccdproc.combine(flat_list, method="median", unit="adu", mem_limit=6e9)

		elif method == "mean":
			print("Combining flats by mean")
			combined_flat = ccdproc.combine(flat_list, method="mean", unit="adu", mem_limit=6e9)

		else:
			print("Combining flats by median")
			combined_flat = ccdproc.combine(flat_list, method="median", unit="adu", mem_limit=6e9)

		print("Opening master dark frame")
		master_dark = ccdproc.fits_ccddata_reader(dark_dir + "/master-dark.fit")

		print("Subtracting master dark from combined flat")
		master_flat = ccdproc.subtract_dark(combined_flat, master_dark, data_exposure=combined_flat.header["exposure"]*u.second, dark_exposure=master_dark.header["exposure"]*u.second, scale=True)

		print("Reading master flat data")
		master_flat_data = np.asarray(master_flat)

		print("Creating normalized flatfield")
		flatfield_data = master_flat_data / np.mean(master_flat_data)

		print("Converting flatfield data to CCDData")
		flatfield = ccdproc.CCDData(flatfield_data, unit="adu")

		return flatfield

	def combine_stack(self, stack_dir, method="median"):

		if method == "median":
			print("Combining stack by median")
			stack = ccdproc.combine(stack_list, method="median", unit="adu", mem_limit=6e9)

		elif method == "mean":
			print("Combining stack by mean")
			stack = ccdproc.combine(stack_list, method="mean", unit="adu", mem_limit=6e9)

		elif method == "sum":
			print("Combining stack by sum")
			stack = ccdproc.combine(stack_list, method="sum", unit="adu", mem_limit=6e9)

		else:
			print("Combining stack by median")
			stack = ccdproc.combine(stack_list, method="median", unit="adu", mem_limit=6e9)

		return stack

	def plate_solve(self, object_frame, output_dir, search=None):

		print("Defining astrometry file names")
		file_name = object_frame[:-4]
		file_axy = file_name + ".axy"
		file_corr = file_name + ".corr"
		file_match = file_name + ".match"
		file_new = file_name + ".new"
		file_rdls = file_name + ".rdls"
		file_solved = file_name + ".solved"
		file_wcs = file_name + ".wcs"
		file_xyls = file_name + "-indx.xyls"

		if search == None:
			print("Running astrometry on", object_frame)
			subprocess.run(["solve-field", "--no-plots", object_frame])

		else:
			ra = search[0]
			dec = search[1]
			radius = search[2]

			print("Running astrometry on", object_frame)
			subprocess.run(["solve-field", "--no-plots", object_frame, "--ra", ra, "--dec", dec, "--radius", radius])

		print("Cleaning up")
		subprocess.run(["rm", file_axy])
		subprocess.run(["rm", file_corr])
		subprocess.run(["rm", file_match])
		subprocess.run(["rm", file_rdls])
		subprocess.run(["rm", file_solved])
		subprocess.run(["rm", file_wcs])
		subprocess.run(["rm", file_xyls])
		subprocess.run(["mv", file_new, "wcs-" + str(file_name) + ".fit"])

		return

	def reduce_object(self, object_frame, flatfield, master_dark, bkg_method="mesh"):

		print("Opening object frame", object_frame)
		obj_frame = fits.open(object_frame)
		obj_frame_data = obj_frame[0].data
		obj_frame_header = obj_frame[0].header

		# Subtract master dark
		print("Opening master dark frame")
		master_dark = fits.open(master_dark)
		master_dark_data = master_dark[0].data
		master_dark_header = master_dark[0].header

		print("Subtracting master dark from object")
		reduced_obj_frame_data = obj_frame_data - master_dark_data

		# Divide by flatfield
		print("Opening flatfield frame")
		flatfield = fits.open(flatfield)
		flatfield_data = flatfield[0].data
		flatfield_header = flatfield[0].header
		
		print("Dividing object by flatfield")
		reduced_obj_frame_data /= flatfield_data

		# Remove cosmic rays
		#sepmed = False
		#cleantype = "medmask"

		#print("Detecting cosmic rays")
		#artifact_mask, reduced_obj_frame_data = astroscrappy.detect_cosmics(reduced_obj_frame_data, sepmed=sepmed, cleantype=cleantype)

		# Subtract background
		if bkg_method == "mesh":

			nsigma = 2.0
			npixels = 5
			dilate_size = 31

			print("Creating mask")
			mask = make_source_mask(reduced_obj_frame_data, nsigma=nsigma, npixels=npixels, dilate_size=dilate_size)

			print("Subtracting background mesh")
			background = sep.Background(reduced_obj_frame_data, mask=mask)
			reduced_obj_frame_data -= background

		elif bkg_method == "sigma":

			print("Subtracting sigma-clipped background")
			mean, median, std = sigma_clipped_stats(reduced_obj_frame_data, sigma=bkg_sigma)
			reduced_obj_frame_data -= median

		print("Converting reduced array to FITS")
		reduced_hdu = fits.PrimaryHDU(reduced_obj_frame_data, header=obj_frame_header)

		return reduced_hdu

if __name__ == "__main__":

	os.system("clear")
	print("Running CAL test")
	start_time = time.time()

	config = configparser.ConfigParser()
	config.read("config.ini")

	pipeline = Pipeline()

	# Combine flat darks
	dark_flat_dir = config["Test"]["dark_flat_dir"]
	dark_flat_path = dark_flat_dir + "/master-dark.fit"

	if os.path.isfile(dark_flat_dir + "/master-dark.fit"):
		print("Reading pre-existing master dark")
		master_dark_flat = fits.open(dark_flat_dir + "/master-dark.fit")

	else:
		master_dark_flat = pipeline.combine_darks(dark_flat_dir)
		print("Writing master dark to output directory")
		ccdproc.fits_ccddata_writer(master_dark_flat, dark_flat_path, overwrite=True)

	# Combine object darks
	dark_obj_dir = config["Test"]["dark_obj_dir"]
	dark_obj_path = dark_obj_dir + "/master-dark.fit"

	if os.path.isfile(dark_obj_path):
		print("Reading pre-existing master dark")
		master_dark_obj = fits.open(dark_obj_path)

	else:
		master_dark_obj = pipeline.combine_darks(dark_obj_dir)
		print("Writing master dark to output directory")
		ccdproc.fits_ccddata_writer(master_dark_obj, dark_obj_path, overwrite=True)

	# Combine flats
	flat_dir = config["Test"]["flat_dir"]
	flat_path = flat_dir + "/flatfield.fit"

	if os.path.isfile(flat_path):
		print("Reading pre-existing flatfield")
		flatfield = fits.open(flat_path)

	else:
		flatfield = pipeline.combine_flats(flat_dir, dark_flat_dir)
		print("Writing flatfield to output directory")
		ccdproc.fits_ccddata_writer(flatfield, flat_path, overwrite=True)

	# Reduce objects
	obj_dir = config["Test"]["obj_dir"]
	
	os.chdir(obj_dir)
	obj_list = []
	for item in glob.glob("*.fit"):

		if "reduced" in item:
			print("Not adding item", item, "to reduction queue")

		else:
			print("Adding", item, "to reduction queue")
			obj_list.append(item)

	obj_list = sorted(obj_list)
	for obj in obj_list:

		if os.path.isfile("reduced-" + obj):
			print("Skipping reduction on", obj)

		else:
			reduced_frame = pipeline.reduce_object(obj, flat_path, dark_obj_path)
			reduced_frame.writeto(obj_dir, overwrite=True)

	# Plate solve objects
	plate_solve_list = []

	for item in glob.glob("reduced*.fit"):
		print("Adding", item, "to plate solve queue")
		plate_solve_list.append(item)

	plate_solve_list = sorted(plate_solve_list)

	for obj in plate_solve_list:

		if os.path.isfile("wcs-" + obj):
			print("Skipping plate solve on", obj)

		else:
			pipeline.plate_solve(obj, obj_dir, search=["03:27:58.39", "-37:09:00.30", "1"])

	# Align objects
	align_list = []

	for item in glob.glob("wcs*.fit"):
		print("Adding", item, "to align queue")
		align_list.append(item)

	align_list = sorted(align_list)

	pipeline.align(align_list, obj_dir, method="reproject")

	# Stack aligned objects
	stack_list = []

	for item in glob.glob("a-wcs-reduced-*.fit"):
		print("Adding", item, "to stack queue")
		stack_list.append(item)

	stack_list = sorted(stack_list)

	if os.path.isfile("stack.fit"):
		print("Reading pre-existing stack")
		stack = fits.open("stack.fit")

	else:
		stack = pipeline.combine_stack(obj_dir)
		print("Writing stack to output directory")
		ccdproc.fits_ccddata_writer(stack, obj_dir + "/stack.fit", overwrite=True)

	end_time = time.time()
	total_time = end_time - start_time
	print("CAL test ended in", "%.1f" % total_time, "seconds")