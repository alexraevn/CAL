from setuptools import setup

setup(
	name="CAL",
	version="0.0.1",
	author="Richard Camuccio",
	author_email="rcamuccio@gmail.com",
	description="CTMO Analysis Library",
	py_modules=["do_align", "do_background_sub", "do_calibrate", "do_cosmicray_detect", "do_dark_master", "do_flat_master", "do_frame_sub", "do_read", "do_source_extract", "do_stack", "do_wcs_attach" ],
	test_suite="tests",
	install_requires=["astroalign >= 1.0.3", "astropy >= 3.1.2", "astroscrappy >= 1.0.8", "ccdproc >= 1.3.0.post1", "numpy >= 1.16.4", "photutils >= 0.6"]
)