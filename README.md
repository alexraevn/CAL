# CAL

The CTMO analysis library (CAL) is a collection of functions used for developing astronomical data anaylsis pipelines for the Cristina Torres Memorial Observatory. The function library is written primarily in Python. The library includes a set of prepared scripts for specific data analysis situations.

***

## Installation

To install use pip from the directory containing `setup.py`.

	$ pip install .

## Usage

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

### Example: [do_dark_master]

To use the function [do_dark_master], import the module

	>>> import do_dark_master as ddm
	>>> ddm.do_dark_master(dark_list, input_dir, output_dir)

where, for example, `dark_list = ["dark-001.fit", "dark-002.fit", ...]`, `input_dir = "/home/username/Documents"`, and `output_dir = "/home/username/Downloads"`.

To use as a script, execute from the command line

	$ python3 do_dark_master.py

where the input and output directories are read from the `config.ini` and the dark list is populated by assuming the specified input diretory only contains a series of dark frames.

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


```
[root_path]
    |--- [dark]
    |    |--- [int_1]
    |    |    |--- {dark-001.fit
    |    |    |--- dark-002.fit
    |    |    |--- ...
    |    |    |+++ master-dark.fit
    |    |
    |    |--- [int_2]
    |    |    |--- dark-001.fit
    |    |    |--- dark-002.fit
    |    |    |--- ...
    |    |    |+++ master-dark.fit
    |    |
    |    |--- ...
    ]    |
    |--- [flat]
    |    |--- [filter_1]
    |    |    |--- flat-001.fit
    |    |    |--- flat-002.fit
    |    |    |--- ...
    |    |    |+++ flatfield.fit
    |    |
    |    |--- [filter_2]
    |    |    |--- flat-001.fit
    |    |    |--- flat-002.fit
    |    |    |--- ...
    |    |    |+++ flatfield.fit
    |    |
    |    |--- ...
    |
    |--- [object_1]
    |    |--- [filter_1]
    |    |    |--- [raw]
    |    |    |    |--- object_1-001.fit
    |    |    |    |--- object_1-002.fit
    |    |    |    |--- ...
    |    |    |
    |    |    |+++ [cal]
    |    |    |    |+++ cal-object_1-001.fit
    |    |    |    |+++ cal-object_1-002.fit
    |    |    |    |+++ ...
    |    |    |
    |    |    |+++ [reject]
    |    |    |    |+++ ...
    |    |    |
    |    |    |+++ [wcs]
    |    |    |    |+++ wcs-object_1-001.fit
    |    |    |    |+++ wcs-object_1-002.fit
    |    |    |    |+++ ...
    |    |    |
    |    |    |+++ [align]
    |    |    |    |+++ a-object_1-001.fit
    |    |    |    |+++ a-object_1-002.fit
    |    |    |    |+++ ...
    |    |    |
    |    |    |+++ stack.fit
    |    |
    |    |--- [filter_2]
    |    |    |--- [raw]
    |    |    |    |--- object_1-001.fit
    |    |    |    |--- object_1-002.fit
    |    |    |    |--- ...
    |    |    |
    |    |    |+++ [cal]
    |    |    |    |+++ cal-object_1-001.fit
    |    |    |    |+++ cal-object_1-002.fit
    |    |    |    |+++ ...
    |    |    |
    |    |    |+++ [reject]
    |    |    |    |+++ ...
    |    |    |
    |    |    |+++ [wcs]
    |    |    |    |+++ wcs-object_1-001.fit
    |    |    |    |+++ wcs-object_1-002.fit
    |    |    |    |+++ ...
    |    |    |
    |    |    |+++ [align]
    |    |    |    |+++ a-object_1-001.fit
    |    |    |    |+++ a-object_1-002.fit
    |    |    |    |+++ ...
    |    |    |
    |    |    |+++ stack.fit
    |
    |--- [object_2]
    |    |--- ...
    |
    |--- ...
```