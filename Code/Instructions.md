# Instructions

- An official data request and account has to be created at [http://www.eorc.jaxa.jp/ALOS/en/palsar_fnf/fnf_index.htm](http://www.eorc.jaxa.jp/ALOS/en/palsar_fnf/fnf_index.htm)

- Full FNF tiles have to be downloaded and stored in a folder (called ALOS_PALSAR/FNF in this example).

- Open the script calcMetric.py and adjust the parameters at the start. 

- Run calcMetric.py on UNIX machine and make sure that you have the necessary libraries installed (gdal,numpy,scipy,rasterio). This script might run on a windows operating system as well, probably needs further adjustment

- Details on methodology and the original python script can be found in a github repository ( https://github.com/Martin-Jung/LecoS ) or in Jung et al. (2016)


*References*

Jung, M. (2016). LecoS — A python plugin for automated landscape ecology analysis. Ecological Informatics, 31, 18–21. [http://doi.org/10.1016/j.ecoinf.2015.11.006](http://doi.org/10.1016/j.ecoinf.2015.11.006)