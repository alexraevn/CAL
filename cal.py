# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CTMO Analysis Library

Date: 7 Jun 2019
Last update: 10 Jul 2020

"""

__author__ = "Richard Camuccio"
__version__ = "2.0.0"

import astroalign as aa 
import astroscrappy
import ccdproc
import configparser
import glob
import math
import matplotlib.pyplot as plt
import numpy as np 
import os
import sep
import subprocess
import time
from astropy import units as u
from astropy.coordinates import AltAz, EarthLocation, SkyCoord
from astropy.io import fits 
from astropy.stats import sigma_clipped_stats
from astropy.time import Time
from photutils import make_source_mask
from reproject import reproject_interp

class Pipeline:

	def __init__(self):

		self.__name = "cal_pipeline"

	def __str__(self):

		return self.__name

	def get_name(self):

		return self.__name

	def align_objects(self, object_list, output_dir, method):
		"""Align a series of frames to a reference frame via ASTROALIGN or WCS REPROJECTION"""

		if len(object_list) == 0 or len(object_list) == 1:

			print("Insufficient number of images for alignment")

		else:

			print("Opening reference frame", object_list[0])
			reference_frame = fits.open(object_list[0])
			reference_data = reference_frame[0].data
			reference_header = reference_frame[0].header

			print("Converting reference data to FITS")
			reference_hdu = fits.PrimaryHDU(reference_data, header=reference_header)

			print("Writing reference frame to output directory")
			reference_hdu.writeto(output_dir + "/a-" + str(object_list[0]), overwrite=True)

			for i in range(1, len(object_list)):

				if os.path.isfile("a-" + object_list[i]):

					print("Skipping align on", object_list[i])

				else:

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

	def combine_darks(self, dark_list, method="median"):
		"""Combine a series of dark frames into a master dark via CCDPROC"""

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

	def combine_flats(self, flat_list, master_dark, method="median"):
		"""Combine and reduce a series of flat frames into a normalized flatfield via CCDPROC"""

		if method == "median":
			print("Combining flats by median")
			combined_flat = ccdproc.combine(flat_list, method="median", unit="adu", mem_limit=6e9)

		elif method == "mean":
			print("Combining flats by mean")
			combined_flat = ccdproc.combine(flat_list, method="mean", unit="adu", mem_limit=6e9)

		else:
			print("Combining flats by median")
			combined_flat = ccdproc.combine(flat_list, method="median", unit="adu", mem_limit=6e9)

		print("Subtracting master dark from combined flat")
		master_flat = ccdproc.subtract_dark(combined_flat, master_dark, data_exposure=combined_flat.header["exposure"]*u.second, dark_exposure=master_dark.header["exposure"]*u.second, scale=True)

		print("Reading master flat data")
		master_flat_data = np.asarray(master_flat)

		print("Creating normalized flatfield")
		flatfield_data = master_flat_data / np.mean(master_flat_data)

		print("Converting flatfield data to CCDData")
		flatfield = ccdproc.CCDData(flatfield_data, unit="adu")

		return flatfield

	def combine_stack(self, stack_list, method="median"):
		"""Combine a series of aligned object frames into a master stack via CCDPROC"""

		if method == "median":
			print("Combining stack by median")
			stack = ccdproc.combine(stack_list, method="median", unit="adu", mem_limit=2e9)

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

	def extract_sources(self, object_frame):

		object_name = object_frame[:-4]

		# Default parameters file
		print("Writing parameters file")
		param_number = "NUMBER"
		param_alphapeak_j2000 = "ALPHAPEAK_J2000"
		param_deltapeak_j2000 = "DELTAPEAK_J2000"
		param_flux_growth = "FLUX_GROWTH"
		param_fluxerr_best = "FLUXERR_BEST"
		param_flux_growthstep = "FLUX_GROWTHSTEP"
		param_fwhm_image = "FWHM_IMAGE"
		param_fwhm_world = "FWHM_WORLD"

		default_parameters = [param_number, param_alphapeak_j2000, param_deltapeak_j2000, param_flux_growth, param_fluxerr_best, param_flux_growthstep, param_fwhm_image, param_fwhm_world]

		default_param = open("default.param", "w")
		for param in default_parameters:
			default_param.write(param + "\n")
		default_param.close()

		# Default configuration file for SExtractor 2.12.4
		# EB 2010-10-10

		print("Writing configuration file")

		# Catalog
		catalog_name = ["CATALOG_NAME", object_name + ".cat"]
		catalog_type = ["CATALOG_TYPE", "ASCII_HEAD"]
		parameters_name = ["PARAMETERS_NAME", "default.param"]

		# Extraction
		detect_type = ["DETECT_TYPE", "CCD"] # CCD (linear) or PHOTO (with gamma correction)
		detect_minarea = ["DETECT_MINAREA", "3"] # min. # of pixels above threshold
		detect_thresh = ["DETECT_THRESH", "5.0"] # <sigmas> or <threshold>,<ZP> in mag.arcsec-2
		analysis_thresh = ["ANALYSIS_THRESH", "5.0"] # <sigmas> or <threshold>,<ZP> in mag.arcsec-2
		detection_filter = ["FILTER", "Y"] # apply filter for detection (Y or N)?
		detection_filter_name = ["FILTER_NAME", "default.conv"]	# name of the file containing the filter
		deblend_nthresh = ["DEBLEND_NTHRESH", "32"]	# Number of deblending sub-thresholds
		deblend_mincont = ["DEBLEND_MINCONT", "0.005"] # Minimum contrast parameter for deblending
		clean = ["CLEAN", "Y"] # Clean spurious detections? (Y or N)?
		clean_param = ["CLEAN_PARAM", "1.0"] # Cleaning efficiency

		# WEIGHTing
		weight_type = ["WEIGHT_TYPE", "NONE"] # type of WEIGHTing: NONE, BACKGROUND, MAP_RMS, MAP_VAR or MAP_WEIGHT
		weight_image = ["WEIGHT_IMAGE", "weight.fits"] # weight-map filename

		# FLAGging
		flag_image = ["FLAG_IMAGE", "flag.fits"] # filename for an input FLAG-image
		flag_type = ["FLAG_TYPE", "OR"] # flag pixel combination: OR, AND, MIN, MAX or MOST

		# Photometry
		phot_apertures = ["PHOT_APERTURES", "20"] # MAG_APER aperture diameter(s) in pixels
		phot_autoparams = ["PHOT_AUTOPARAMS", "2.5", "3.5"] # MAG_AUTO parameters: <Kron_fact>,<min_radius>
		phot_petroparams = ["PHOT_PETROPARAMS", "2.0", "3.5"] # MAG_PETRO parameters: <Petrosian_fact>,<min_radius>
		phot_autoapers = ["PHOT_AUTOAPERS", "0.0", "0.0"] # <estimation>,<measurement> minimum apertures for MAG_AUTO and MAG_PETRO
		satur_level = ["SATUR_LEVEL", "65535.0"] # level (in ADUs) at which arises saturation
		satur_key = ["SATUR_KEY", "SATURATE"] # keyword for saturation level (in ADUs)
		mag_zeropoint = ["MAG_ZEROPOINT", "0.0"] # magnitude zero-point
		mag_gamma = ["MAG_GAMMA", "4.0"] # gamma of emulsion (for photographic scans)
		gain = ["GAIN", "1.39"]	# keyword for detector gain in e-/ADU
		gain_key = ["GAIN_KEY", "GAIN"]	# keyword for detector gain in e-/ADU
		pixel_scale = ["PIXEL_SCALE", "0"] # size of pixel in arcsec (0=use FITS WCS info)

		# Star/Galaxy Separation
		seeing_fwhm = ["SEEING_FWHM", "6.0"] # stellar FWHM in arcsec
		starnnw_name = ["STARNNW_NAME", "default.nnw"] # Neural-Network_Weight table filename

		# Background
		back_type = ["BACK_TYPE", "AUTO"] # AUTO or MANUAL
		back_value = ["BACK_VALUE", "0.0"] # Default background value in MANUAL mode
		back_size = ["BACK_SIZE", "64"]	# Background mesh: <size> or <width>,<height>
		back_filtersize = ["BACK_FILTERSIZE", "3"] # Background filter: <size> or <width>,<height>

		# Check Image
		checkimage_type = ["CHECKIMAGE_TYPE", "NONE"] # can be NONE, BACKGROUND, BACKGROUND_RMS, MINIBACKGROUND, MINIBACK_RMS, -BACKGROUND, FILTERED, OBJECTS, -OBJECTS, SEGMENTATION, or APERTURES
		checkimage_name = ["CHECKIMAGE_NAME", "check.fits"] # Filename for the check-image

		# Memory (change with caution!)
		memory_objstack = ["MEMORY_OBJSTACK", "3000"] # number of objects in stack
		memory_pixstack = ["MEMORY_PIXSTACK", "300000"]	# number of pixels in stack
		memory_bufsize = ["MEMORY_BUFSIZE", "1024"] # number of lines in buffer

		# ASSOCiation
		assoc_name = ["ASSOC_NAME", "sky.list"]	# name of the ASCII file to ASSOCiate
		assoc_data = ["ASSOC_DATA", "2", "3", "4"] # columns of the data to replicate (0=all)
		assoc_params = ["ASSOC_PARAMS", "2", "3", "4"] # columns of xpos,ypos[,mag]
		assoc_radius = ["ASSOC_RADIUS", "2.0"] # cross-matching radius (pixels)
		assoc_type = ["ASSOC_TYPE", "NEAREST"] # ASSOCiation method: FIRST, NEAREST, MEAN, MAG_MEAN, SUM, MAG_SUM, MIN or MAX
		assocselec_type = ["ASSOCSELEC_TYPE", "MATCHED"] # ASSOC selection type: ALL, MATCHED or -MATCHED

		# Miscellaneous
		verbose_type = ["VERBOSE_TYPE", "NORMAL"] # can be QUIET, NORMAL or FULL
		header_suffix = ["HEADER_SUFFIX", ".head"] # Filename extension for additional headers
		write_xml = ["WRITE_XML", "N"]# Write XML file (Y/N)?
		xml_name = ["XML_NAME", "sex.xml"] # Filename for XML output
		xsl_url = ["XSL_URL", "file:///usr/local/share/sextractor/sextractor.xsl"] # Filename for XSL style-sheet

		config_parameters = [catalog_name, catalog_type, parameters_name, detect_type, detect_minarea, detect_thresh,
					analysis_thresh, detection_filter, detection_filter_name, deblend_nthresh, deblend_mincont, 
					clean, clean_param, weight_type, weight_image, flag_image, flag_type, phot_apertures, 
					phot_autoparams, phot_petroparams, phot_autoapers, satur_level, satur_key, mag_zeropoint,
					mag_gamma, gain, gain_key, pixel_scale, seeing_fwhm, starnnw_name, back_type, back_value,
					back_size, back_filtersize, checkimage_type, checkimage_name, memory_objstack, memory_pixstack,
					memory_bufsize, assoc_name, assoc_data, assoc_params, assoc_radius, assoc_type, assocselec_type,
					verbose_type, header_suffix, write_xml, xml_name, xsl_url]

		default_sex = open("default.sex", "w")
		for param in config_parameters:
			for item in param:
				default_sex.write(item + " ")
			default_sex.write("\n")
		default_sex.close()

		# Default convolution file 
		print("Writing convolution file")
		conv_norm_1 = "CONV NORM\n"
		conv_norm_2 = "# 3x3 ``all-ground'' convolution mask with FWHM = 2 pixels.\n"
		conv_norm_3 = "1 2 1\n"
		conv_norm_4 = "2 4 2\n"
		conv_norm_5 = "1 2 1"

		conv_norm_lines = [conv_norm_1, conv_norm_2, conv_norm_3, conv_norm_4, conv_norm_5]

		default_conv = open("default.conv", "w")
		for line in conv_norm_lines:
			default_conv.write(line)
		default_conv.close()

		# Default neural network weights file
		print("Writing neural network weights file")
		nnw_1 = "NNW\n"
		nnw_2 = "# Neural Network Weights for the SExtractor star/galaxy classifier (V1.3)\n"
		nnw_3 = "# inputs:	9 for profile parameters + 1 for seeing.\n"
		nnw_4 = "# outputs:	``Stellarity index'' (0.0 to 1.0)\n"
		nnw_5 = "# Seeing FWHM range: from 0.025 to 5.5'' (images must have 1.5 < FWHM < 5 pixels)\n"
		nnw_6 = "# Optimized for Moffat profiles with 2<= beta <= 4.\n\n"
		nnw_7 = " 3 10 10 1\n\n"
		nnw_8 = "-1.56604e+00 -2.48265e+00 -1.44564e+00 -1.24675e+00 -9.44913e-01 -5.22453e-01  4.61342e-02  8.31957e-01  2.15505e+00  2.64769e-01\n"
		nnw_9 = " 3.03477e+00  2.69561e+00  3.16188e+00  3.34497e+00  3.51885e+00  3.65570e+00  3.74856e+00  3.84541e+00  4.22811e+00  3.27734e+00\n\n"
		nnw_10 = "-3.22480e-01 -2.12804e+00  6.50750e-01 -1.11242e+00 -1.40683e+00 -1.55944e+00 -1.84558e+00 -1.18946e-01  5.52395e-01 -4.36564e-01 -5.30052e+00\n"
		nnw_11 = " 4.62594e-01 -3.29127e+00  1.10950e+00 -6.01857e-01  1.29492e-01  1.42290e+00  2.90741e+00  2.44058e+00 -9.19118e-01  8.42851e-01 -4.69824e+00\n"
		nnw_12 = "-2.57424e+00  8.96469e-01  8.34775e-01  2.18845e+00  2.46526e+00  8.60878e-02 -6.88080e-01 -1.33623e-02  9.30403e-02  1.64942e+00 -1.01231e+00\n"
		nnw_13 = " 4.81041e+00  1.53747e+00 -1.12216e+00 -3.16008e+00 -1.67404e+00 -1.75767e+00 -1.29310e+00  5.59549e-01  8.08468e-01 -1.01592e-02 -7.54052e+00\n"
		nnw_14 = " 1.01933e+01 -2.09484e+01 -1.07426e+00  9.87912e-01  6.05210e-01 -6.04535e-02 -5.87826e-01 -7.94117e-01 -4.89190e-01 -8.12710e-02 -2.07067e+01\n"
		nnw_15 = "-5.31793e+00  7.94240e+00 -4.64165e+00 -4.37436e+00 -1.55417e+00  7.54368e-01  1.09608e+00  1.45967e+00  1.62946e+00 -1.01301e+00  1.13514e-01\n"
		nnw_16 = " 2.20336e-01  1.70056e+00 -5.20105e-01 -4.28330e-01  1.57258e-03 -3.36502e-01 -8.18568e-02 -7.16163e+00  8.23195e+00 -1.71561e-02 -1.13749e+01\n"
		nnw_17 = " 3.75075e+00  7.25399e+00 -1.75325e+00 -2.68814e+00 -3.71128e+00 -4.62933e+00 -2.13747e+00 -1.89186e-01  1.29122e+00 -7.49380e-01  6.71712e-01\n"
		nnw_18 = "-8.41923e-01  4.64997e+00  5.65808e-01 -3.08277e-01 -1.01687e+00  1.73127e-01 -8.92130e-01  1.89044e+00 -2.75543e-01 -7.72828e-01  5.36745e-01\n"
		nnw_19 = "-3.65598e+00  7.56997e+00 -3.76373e+00 -1.74542e+00 -1.37540e-01 -5.55400e-01 -1.59195e-01  1.27910e-01  1.91906e+00  1.42119e+00 -4.35502e+00\n\n"
		nnw_20 = "-1.70059e+00 -3.65695e+00  1.22367e+00 -5.74367e-01 -3.29571e+00  2.46316e+00  5.22353e+00  2.42038e+00  1.22919e+00 -9.22250e-01 -2.32028e+00\n\n\n"
		nnw_21 = " 0.00000e+00\n"
		nnw_22 = " 1.00000e+00"

		default_nnw_lines = [nnw_1, nnw_2, nnw_3, nnw_4, nnw_5, nnw_6, nnw_7, nnw_8, nnw_9, nnw_10, nnw_11,
					nnw_12, nnw_13, nnw_14, nnw_15, nnw_16, nnw_17, nnw_18, nnw_19, nnw_20, nnw_21, nnw_22]

		default_nnw = open("default.nnw", "w")
		for line in default_nnw_lines:
			default_nnw.write(line)
		default_nnw.close()

		print("Running source extractor on", object_frame)
		subprocess.run(["source-extractor", object_frame])
		subprocess.run(["rm", "default.conv"])
		subprocess.run(["rm", "default.nnw"])

		frame_list = []
		seeing_list = []
		growth_radius_list = []

		catalog = open(object_name + ".cat")

		for line in catalog:
			line = line.split()

			if line[0] == "#":
				pass

			else:
				frame = int(line[0])
				frame_list.append(frame)

				seeing = float(line[7]) * 3600
				seeing_list.append(seeing)

				growth_radius = float(line[5])
				growth_radius_list.append(growth_radius)

		mean_seeing = np.mean(seeing_list)
		mean_growth_radius = np.mean(growth_radius_list)

		return mean_seeing, mean_growth_radius

	def plate_solve(self, object_frame, search=None):

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
			print("Running unconstrained astrometry on", object_frame)
			subprocess.run(["solve-field", "--no-plots", object_frame])

		else:
			ra = search[0]
			dec = search[1]
			radius = search[2]

			print("Running constrained", (ra, dec, radius), "astrometry on", object_frame)
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

		# Flatfield correct
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

	print("Reading configuration file")
	config = configparser.ConfigParser()
	config.read("config.ini")

	print("Initializing pipeline")
	pipeline = Pipeline()

	# --- Combine flat darks
	dark_flat_dir = config["Test"]["dark_flat_dir"]
	dark_flat_path = dark_flat_dir + "/master-dark.fit"

	if os.path.isfile(dark_flat_path):
		print("Reading pre-existing master (flat) dark")
		master_dark_flat = fits.open(dark_flat_path)

	else:
		os.chdir(dark_flat_dir)
		dark_flat_list = []

		for item in glob.glob("*.fit"):
			print("Adding", item, "to dark (flat) list")
			dark_flat_list.append(item)

		master_dark_flat = pipeline.combine_darks(dark_flat_list, method="median")

		print("Writing master (flat) dark to output")
		ccdproc.fits_ccddata_writer(master_dark_flat, dark_flat_path, overwrite=True)

	# --- Combine object darks
	dark_obj_dir = config["Test"]["dark_obj_dir"]
	dark_obj_path = dark_obj_dir + "/master-dark.fit"

	if os.path.isfile(dark_obj_path):

		print("Reading pre-existing master (object) dark")
		master_dark_obj = fits.open(dark_obj_path)

	else:

		os.chdir(dark_obj_dir)
		dark_obj_list = []

		for item in glob.glob("*.fit"):
			print("Adding", item, "to dark (object) list")
			dark_obj_list.append(item)

		master_dark_obj = pipeline.combine_darks(dark_obj_list)

		print("Writing master (object) dark to output")
		ccdproc.fits_ccddata_writer(master_dark_obj, dark_obj_path, overwrite=True)

	# --- Combine flats
	flat_dir = config["Test"]["flat_dir"]
	flat_path = flat_dir + "/flatfield.fit"

	if os.path.isfile(flat_path):
		print("Reading pre-existing flatfield")
		flatfield = fits.open(flat_path)

	else:
		print("Opening master dark (flat) frame")
		master_dark = ccdproc.fits_ccddata_reader(dark_flat_path)

		os.chdir(flat_dir)
		flat_list = []

		for item in glob.glob("*.fit"):
			print("Adding", item, "to flat list")
			flat_list.append(item)

		flatfield = pipeline.combine_flats(flat_list, master_dark, method="median")

		print("Writing flatfield to output")
		ccdproc.fits_ccddata_writer(flatfield, flat_path, overwrite=True)

	# --- Reduce objects
	obj_dir = config["Test"]["obj_dir"]
	
	os.chdir(obj_dir)
	obj_list = []

	for item in glob.glob("*.fit"):

		if "reduced" in item:
			print("Not adding", item, "to reduction queue")

		elif "wcs-reduced" in item:
			print("Not adding", item, "to reduction queue")

		elif "a-wcs-reduced" in item:
			print("Not adding", item, "to reduction queue")

		elif "stack" in item:
			print("Not adding", item, "to reduction queue")

		else:
			print("Adding", item, "to reduction queue")
			obj_list.append(item)

	obj_list = sorted(obj_list)

	for obj in obj_list:

		if os.path.isfile("reduced-" + obj):
			print("Skipping reduction on", obj)

		else:
			reduced_frame = pipeline.reduce_object(obj, flat_path, dark_obj_path, bkg_method="mesh")

			print("Writing", obj, "to output")
			reduced_frame.writeto(obj_dir + "/reduced-" + obj, overwrite=True)

	# --- Plate solve objects
	plate_solve_list = []

	for item in glob.glob("reduced*.fit"):
		print("Adding", item, "to plate solve queue")
		plate_solve_list.append(item)

	plate_solve_list = sorted(plate_solve_list)

	for obj in plate_solve_list:

		if os.path.isfile("wcs-" + obj):
			print("Skipping plate solve on", obj)

		else:
			pipeline.plate_solve(obj, search=["00:40:19.748", "40:49:35.98", "1"])

	# --- Align objects
	align_list = []

	for item in glob.glob("wcs*.fit"):
		print("Adding", item, "to align queue")
		align_list.append(item)

	align_list = sorted(align_list)

	pipeline.align_objects(align_list, obj_dir, method="reproject")

	# --- Stack aligned objects
	stack_list = []

	for item in glob.glob("a-wcs-reduced-*.fit"):
		print("Adding", item, "to stack queue")
		stack_list.append(item)

	stack_list = sorted(stack_list)

	if os.path.isfile("stack.fit"):
		print("Reading pre-existing stack")
		stack = ccdproc.fits_ccddata_reader("stack.fit")

	else:
		stack = pipeline.combine_stack(stack_list)
		print("Writing stack to output directory")
		ccdproc.fits_ccddata_writer(stack, obj_dir + "/stack.fit", overwrite=True)

	mean_seeing, mean_growth_radius = pipeline.extract_sources("stack.fit")

	print("Mean seeing:", mean_seeing, "arcsec")
	print("Mean growth radius:", mean_growth_radius, "px")

	# --- Photometry on image series
	altitude_list = []
	seeing_list = []
	time_list = []

	observation_location = EarthLocation(lat="-31.5983", lon="-64.5439")

	for item in stack_list:

		# --- Read FITS header
		image = fits.open(item)
		image_header = image[0].header

		image_dateobs = image_header["DATE-OBS"]
		#image_timeobs = image_header["TIME-OBS"]
		image_jd = image_header["JD"]
		image_ra = image_header["CRVAL1"]
		image_dec = image_header["CRVAL2"]

		# --- Time
		observation_time = Time(image_dateobs) #+ " " + image_timeobs)
		time_list.append(image_jd)

		# --- Air mass
		aa = AltAz(location=observation_location, obstime=observation_time)
		coord = SkyCoord(str(image_ra), str(image_dec), unit="deg")
		coord_transform = coord.transform_to(aa)
		h = coord_transform.alt.degree
		altitude_list.append(h)

		zenith_distance_list = []
		for h in altitude_list:
			z = 90 - h
			zenith_distance_list.append(z)

		airmass_list = []
		for z in zenith_distance_list:
			x = 1 / (math.cos(math.radians(z)) + 0.50572*((6.07995 + 90 - z)**-1.6364)) # Kasten and Young (1994) method
			airmass_list.append(x)

		# --- Seeing
		seeing, growth_radius = pipeline.extract_sources(item)
		seeing_list.append(seeing)

	plt.clf()
	font = {"fontname":"Monospace", "size":10}
	plt.plot(time_list, airmass_list)
	plt.title("Air mass", **font)
	plt.xlabel("Time [JD]", **font)
	plt.ylabel("Air mass", **font)
	plt.xticks(**font)
	plt.yticks(**font)
	plt.savefig("airmass.png", dpi=300)

	plt.clf()
	font = {"fontname":"Monospace", "size":10}
	plt.plot(time_list, seeing_list, ".")
	plt.title("Seeing", **font)
	plt.xlabel("Time [JD]", **font)
	plt.ylabel("Mean FWHM [arcsec]", **font)
	plt.xticks(**font)
	plt.yticks(**font)
	plt.savefig("seeing.png", dpi=300)

	end_time = time.time()
	total_time = end_time - start_time
	print("CAL test ended in", "%.1f" % total_time, "seconds")
