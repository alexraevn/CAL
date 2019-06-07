# CAL

The CTMO analysis library (CAL) is a collection of scripts for developing pipelines in astronomical data analysis. These scripts, each containing a primary, unique function, are written primarily in Python. The library includes a set of scripts, composed of these functions, for various and specific data analysis situations.

Function library currently includes:

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

The Transient Optical Follow-Up (TOFU) pipeline serves to analyze optical image data (FITS files) taken by telescopes in response to gravitational wave triggers by the LIGO and Virgo observatories.

The Teaspoon (TSP) pipeline is used for generating light curves for a given source in a time series of FITS frames.