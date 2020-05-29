# !/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
	name="CAL",
	version="2.0.0",
	author="Richard Camuccio",
	author_email="rcamuccio@gmail.com",
	description="CTMO analysis library",
	py_modules=["align",
		"background_subtract",
		"combine_darks",
		"combine_flats",
		"mask_fits",
		"plate_solve",
		"read_fits",
		"reduce_objects",
		"remove_artifacts",
		"subtract",
		"trim_fits"]
	install_requires=["astroalign >= 2.0.2", 
		"astropy >= 4.0.1.post1",
		"astroscrappy >= 1.0.8", 
		"ccdproc >= 2.1.0", 
		"fitsio >= 1.1.2",
		"numpy >= 1.18.4", 
		"photutils >= 0.7.2",
		"reproject >= 0.7",
		"sep >= 1.0.3"]
)