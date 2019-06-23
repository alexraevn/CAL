# CAL

The CTMO analysis library (CAL) is a collection of functions used for developing astronomical data anaylsis pipelines for the Cristina Torres Memorial Observatory. The function library is written primarily in Python. The library includes a set of prepared scripts for specific data analysis situations.

***

### Installation

To install use pip from the directory containing `setup.py`.

	$ pip install .

### Usage

***

The function library currently includes

	[do_align]
	[do_background_sub]
	[do_calibrate]
	[do_cosmicray_detect]
	[do_dark_master]
	[do_flat_master]
	[do_frame_sub]
	[do_read]
	[do_source_extract]
	[do_stack]
	[do_wcs_attach]

***

The Transient Optical Follow-Up (TOFU) pipeline serves to analyze optical image data (FITS files) taken by telescopes in response to gravitational wave triggers by the LIGO and Virgo observatories.

The TOFU pipeline is run as a script from the terminal

	$ python3 tofu.py

with the file structure and other parameters read from the tofu.ini configuration file.

***

The Teaspoon (TSP) pipeline is used for generating light curves for a given source in a time series of FITS frames.

The TSP pipeline is run as a script from the terminal

	$ python3 tsp.py

with the file structure and other parameters read from the tsp.ini configuration file.

***

7 Jun 2019

Last update: 23 Jun 2019

Richard Camuccio

richard.camuccio01@utrgv.edu