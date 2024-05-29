# The Arctic Retrogressive Thaw Slumps Data Set (ARTS)

[![DOI](https://zenodo.org/badge/730674203.svg)](https://zenodo.org/doi/10.5281/zenodo.10535025)

This repository hosts:
1. The ARTS main data set (current and historical versions)
2. Tutorials (Jupyter Notebook or Rmarkdown) for preparing and formatting contributions to the ARTS data set (ARTS/Tutorial/data_formatting.ipynb or ARTS/Tutorial/data_formatting.Rmd)
3. Tutorial for splitting the ARTS data set into training, validation, and testing subsets for machine learning models while ensuring no data leakage (ARTS/Tutorial/Automated_Training_Validation_Testing_Data_Split.ipynb)

![image](https://github.com/whrc/ARTS/blob/main/img/Yang_RTS_site_figure1_Dec_5_2023%20sm.jpg)

## Instructions for Use
### Load the ARTS from GitHub (Python)
```
import json, requests

# input the ARTS version you want to load:
ARTS_VERSION = 'v.0.0.20-alpha'

# get the main dataset from GitHub
github_url = 'https://raw.githubusercontent.com/whrc/ARTS/main/ARTS_main_dataset/'
main_file_name = 'ARTS_main_dataset.geojson'
url = github_url + ARTS_VERSION + '/' + main_file_name
resp = requests.get(url)
data = json.loads(resp.text)
```
#### Inspect the first data entry
```
data['features'][0]
```
{'type': 'Feature',
 'properties': {'CentroidLat': '71.89659414',
  'CentroidLon': '-120.66907384',
  'RegionName': 'Banks Island, Inuvik Region, Canada',
  'CreatorLab': 'TLantz, University of Victoria',
  'BaseMapDate': '2020-07-05,2020-08-20',
  'BaseMapSource': 'PlanetScope',
  'BaseMapResolution': '3',
  'TrainClass': 'Positive',
  'LabelType': 'Polygon',
  'MergedRTS': None,
  'SplitRTS': None,
  'NewRTS': None,
  'StabilizedRTS': None,
  'UnknownRelationship': None,
  'ContributionDate': '2024-02-01',
  'UID': '6aff1955-71f5-5fa5-97d1-d9e006e4ec5c',
  'BaseMapID': None,
  'Area': None,
  'Notes': 'Headwall to the southwest'},
 'geometry': {'type': 'MultiPolygon',
  'coordinates': [[[[-1915450.9802012292, -489398.3013161274],
     [-1915494.2298194107, -489388.06834635197],
    ...]]]}}

## Steps for contributing to the ARTS data set
**1. Fork this Respository and Clone Your Fork Onto Your Local Machine**

Fork this repository using the **Fork** button in the top right corner in the browser. Next, clone your forked repository. From the forked repository on your github page, copy the URL using the **Code** button in the top right of the browser. From the command line (whichever shell you use for git), navigate to the directory in which you would like to clone the repository (this should be the directory in which you would like to work on this project), and run: `git clone {URL}`.

**2. Set Up a Conda Environment from env.yml**

Make sure you have [Anaconda](https://www.anaconda.com/download/) or [Miniconda](https://docs.conda.io/projects/miniconda/en/latest/) installed. [Mamba](https://anaconda.org/conda-forge/mamba) is also recommended (mamba is not required, but is much faster than conda).

In the command line, make sure you are in the repository directory and run: `mamba env create -f env.yml` (or `conda env create -f env.yml`, if you don't have mamba installed). This will create a conda environment named **rts_dataset**. Run: `conda env list` to ensure that **rts_dataset** shows up.

**3. Run the Scripts (Choose either Rmarkdown or Jupyter Notebook)**

Rmarkdown is preferred, as the step to check for intersections is much faster in R (~40x faster as of v.0.0.20-alpha). (If you have suggestions for speeding up the Python version, please be in touch.) 

Copy your new, pre-formatted RTS file into the **input_data** folder. Take a look at **input_data/metadata_description** for formatting requirements.
   
If using Python, ensure you are in the repository directory and activate the conda environment by running: `conda activate rts_dataset`. Open **Tutorial/rts_dataset_formatting.ipynb** in either Jupyter Notebook or Jupyter Lab by running: `jupyter notebook` or `jupyter lab`. Follow the instructions in the script to format your data set.
   
If using R, open the project, **ARTS.Rproj**, in RStudio. Open **Tutorial/rts_dataset_formatting.Rmd**. Install any missing packages required to run the script. Follow the instructions in the script to format your data set. If you encounter issues during uuid generation, make sure that **rts_dataset** is specified as the python interpreter in the python section of project options (Tools > Project Options > Python).

## Metadata Formatting Summary Example:

| FieldName         | Format                           | Required       | Description                                                                                                                |
|-------------------|----------------------------------|----------------|----------------------------------------------------------------------------------------------------------------------------|
| CentroidLat       | Decimal Degrees                  | TRUE           | Polygon centroid latitude in EPSG:4326                                                                                     |
| CentroidLon       | Decimal Degrees                  | TRUE           | Polygon centroid longitude in EPSG:4326                                                                                    |
| RegionName        | String                           | TRUE           | Name of the geographical region                                                                                            |
| CreatorLab        | String                           | TRUE           | Data creator and associated organization                                                                                   |
| BaseMapDate       | String                           | TRUE           | Date of base map used for RTS delineation in YYYY-MM-DD for a single date, range of dates should be separated by a comma   |
| BaseMapSource     | String                           | TRUE           | Name of the satellite sensor used for RTS digitisation                                                                     |
| BaseMapResolution | Number                           | TRUE           | Resolution of the imagery used for RTS digitisation (meters)                                                               |
| TrainClass        | String                           | TRUE           | 'Positive' for genuine RTS and 'Negative' for background                                                                   |
| LabelType         | String                           | TRUE           | Type of digitisation, e.g. 'Polygon', 'BoundingBox'                                                                        |
| MergedRTS         | String                           | auto-generated | UIDs of intersecting RTS that merged into one RTS                                                                          |
| StabilizedRTS     | String                           | auto-generated | UIDs of intersecting stabilized RTS scars                                                                                  |
| ContributionDate  | String                           | auto-generated | Date of contribution to the ARTS main file in YYYY-MM-DD                                                                   |
| UID               | 36-character alphanumeric string | auto-generated | Unique identifier generated using uuid5 by concatenating all 'Required-True' fields as a single string                   |

## Related Publications
Yang Y, Rodenhizer H, Rogers B M, et al. ARTS: a scalable data set for Arctic Retrogressive Thaw Slumps[R]. Copernicus Meetings, 2024.
(https://meetingorganizer.copernicus.org/EGU24/EGU24-1365.html)

## Selected Data Examples
![image](https://github.com/whrc/ARTS/blob/main/img/RTSfigure.jpg)

