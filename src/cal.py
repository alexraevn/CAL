# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CAL

Date: 26 May 2020
Last update: 29 May 2020

"""

__author__ = "Richard Camuccio"
__version__ = "2.0.0"

import astroalign as aa 
import astroscrappy
import ccdproc
import fitsio
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

	def align(self, object_list, method, output_dir):
		"""Align a series of frames to a reference frame via ASTROALIGN or WCS REPROJECTION"""

		if len(object_list) == 0 or len(object_list) == 1:
			print("Insufficient number of images for alignment")

		else:
			print("Opening reference frame")
			reference_frame = fits.open(object_list[0])

			print("Reading reference data")
			reference_data = reference_frame[0].data

			print("Reading reference header")
			reference_header = reference_frame[0].header

			print("Converting reference data to FITS")
			reference_hdu = fits.PrimaryHDU(reference_data, header=reference_header)

			print("Writing reference frame to output directory")
			reference_hdu.writeto(output_dir + "/a-" + str(object_list[0]))

			for i in range(1, len(object_list)):

				print("Opening target frame", object_list[i])
				target_frame = fits.open(object_list[i])

				print("Reading target data")
				target_data = target_frame[0].data

				print("Reading target header")
				target_header = target_frame[0].header

				if method == "astroalign":

					print("Aligning target frame with reference frame")
					array = aa.register(target_data, reference_data)

				elif method == "reproject":

					print("Converting target data to FITS")
					target_hdu = fits.PrimaryHDU(target_data, header=target_header)

					print("Aligning target frame with reference frame")
					array, footprint = reproject_interp(target_hdu, reference_header)

				print("Converting aligned target data to FITS")
				target_hdu = fits.PrimaryHDU(array, header=reference_header)

				print("Writing aligned frame to output directory")
				target_hdu.writeto(output_dir + "/a-" + str(object_list[i]))

		return

	def background_subtract(self, item, method="mesh"):

		print("Opening FITS frame", item)
		frame = fits.open(item)

		print("Reading FITS data")
		frame_data = frame[0].data

		print("Reading FITS header")
		frame_header = frame[0].header

		if method == "mesh":

			nsigma = 2.0
			npixels = 5
			dilate_size = 31

			print("Creating array mask")
			mask = make_source_mask(frame_data, nsigma=nsigma, npixels=npixels, dilate_size=dilate_size)

			print("Subtracting background mesh")
			background = sep.Background(frame_data, mask=mask)
			reduced_data -= background

		elif method == "sigma":

			print("Subtracting sigma-clipped background")
			mean, median, std = sigma_clipped_stats(frame_data, sigma=bkg_sigma)
			reduced_data -= median

		return reduced_data

	def combine_darks(self, input_dir, output_dir, method="median", write=True):

		if os.path.isfile(output_dir + "/master-dark.fit"):
			print("Reading pre-existing master dark frame")
			master_dark = fits.open(output_dir + "/master-dark.fit")

		else:
			print("Changing to input directory", input_dir)
			os.chdir(input_dir)

			print("Creating dark list")
			dark_list = []

			for item in glob.glob("*.fit"):
				print("Adding", item, "to dark list")
				dark_list.append(item)

			if method == "median":
				print("Combining darks by median")
				master_dark = ccdproc.combine(dark_list, method="median", unit="adu")

			elif method == "mean":
				print("Combining darks by mean")
				master_dark = ccdproc.combine(dark_list, method="mean", unit="adu")

			else:
				print("Combining darks by median")
				master_dark = ccdproc.combine(dark_list, method="median", unit="adu")

			if write == True:

				if not os.path.exists(output_dir):
					print("Creating output directory", output_dir)
					os.makedirs(output_dir)

				print("Writing master dark to output directory")
				ccdproc.fits_ccddata_writer(master_dark, output_dir + "/master-dark.fit")

			else:
				None

		return master_dark

	def combine_flats(self, input_dir, dark_dir, output_dir, method="median", write=True):

		if os.path.exists(output_dir):
			print("Reading pre-existing flatfield frame")
			flatfield = fits.open(output_dir + "/flatfield.fit")

		else:
			print("Changing to input directory")
			os.chdir(input_dir)

			print("Creating flat list")
			flat_list = []

			for item in glob.glob("*.fit"):
				print("Adding", item, "to flat list")
				flat_list.append(item)

			if method == "median":
				print("Combining flats by median")
				combined_flat = ccdproc.combine(flat_list, method="median", unit="adu")

			elif method == "mean":
				print("Combining flats by mean")
				combined_flat = ccdproc.combine(flat_list, method="mean", unit="adu")

			else:
				print("Combining flats by median")
				combined_flat = ccdproc.combine(flat_list, method="median", unit="adu")

			print("Opening master dark frame")
			master_dark = ccdproc.fits_ccddata_reader(dark_dir + "/master-dark.fit")

			print("Subtracting master dark from combined flat")
			master_flat = ccdproc.subtract_dark(combined_flat, master_dark, 
				data_exposure=combined_flat.header["exposure"]*u.second, 
				dark_exposure=master_dark.header["exposure"]*u.second, scale=True)

			print("Reading master flat data")
			master_flat_data = np.asarray(master_flat)

			print("Creating normalized flatfield")
			flatfield_data = master_flat_data / np.mean(master_flat_data)

			print("Converting flatfield data to CCDData")
			flatfield = ccdproc.CCDData(flatfield_data, unit="adu")

			if write == True:

				if not os.path.exists(output_dir):
					print("Creating output directory", output_dir)
					os.makedirs(output_dir)

				print("Writing flatfield to output directory")
				ccdproc.fits_ccddata_writer(flatfield, output_dir + "/flatfield.fit")

			else:
				None

		return flatfield

	def mask_fits(self):

		return

	def plate_solve(self, frame, output_dir, search=None):

		for item in object_list:

			print("Defining astrometry file names")
			file = item[:-4]
			file_axy = file + ".axy"
			file_corr = file + ".corr"
			file_match = file + ".match"
			file_new = file + ".new"
			file_rdls = file + ".rdls"
			file_solved = file + ".solved"
			file_wcs = file + ".wcs"
			file_xyls = file + "-indx.xyls"

			if search == None:
				print("Running astrometry on", item)
				subprocess.run(["solve-field", "--no-plots", item])

			else:
				ra = search[0]
				dec = search[1]
				radius = search[2]

				print("Running astrometry on", item)
				subprocess.run(["solve-field", "--no-plots", item, "--ra", ra, "--dec", dec, "--radius", radius])

			print("Cleaning up")
			subprocess.run(["rm", file_axy])
			subprocess.run(["rm", file_corr])
			subprocess.run(["rm", file_match])
			subprocess.run(["rm", file_rdls])
			subprocess.run(["rm", file_solved])
			subprocess.run(["rm", file_wcs])
			subprocess.run(["rm", file_xyls])

			print("Moving solved field to", output_dir)
			subprocess.run(["mv", file_new, output_dir + str("/wcs-") + file + ".fit"])

		return

	def read_fits(self):

		return

	def reduce_object(self, object_frame, master_dark, flatfield, output_dir):

		return reduced_data

	def remove_artifacts(self, object_frame):

		print("Opening FITS frame")
		frame = fits.open(object_frame)

		print("Reading FITS data")
		frame_data = frame[0].data

		print("Reading FITS header")
		frame_header = frame[0].header

		sepmed = False
		cleantype = "medmask"

		print("Detecting and removing artifacts")
		artifact_mask, reduced_data = astroscrappy.detect_cosmics(frame_data, sepmed=sepmed, cleantype=cleantype)

		return reduced_data, frame_header, artifact_mask

	def subtract(self, method):

		return

	def trim_fits(self):

		return

if __name__ == "__main__":

	os.system("clear")
	print("Running CAL test")
	start_time = time.time()

	pipeline = Pipeline()

	input_dark_dir = "/home/rcamuccio/Documents/CAL/2020-02-28/dark"
	output_dark_dir = "/home/rcamuccio/Documents/CAL/2020-02-28/dark/output"
	master_dark = pipeline.combine_darks(input_dark_dir, output_dark_dir)

	input_flat_dir = "/home/rcamuccio/Documents/CAL/2020-02-28/flat"
	input_dark_dir = "/home/rcamuccio/Documents/CAL/2020-02-28/dark/output"
	output_flat_dir = "/home/rcamuccio/Documents/CAL/2020-02-28/flat/output"
	flatfield = pipeline.combine_flats(input_flat_dir, input_dark_dir, output_flat_dir)

	end_time = time.time()
	total_time = end_time - start_time
	print("Ended in", "%.1f" % total_time, "seconds")