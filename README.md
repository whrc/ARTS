# The Arctic Retrogressive Thaw Slumps Data Set (ARTS)

This repository hosts:
1. The ARTS main data set (current and historical versions)
2. Tutorials/scripts (Jupyter Notebook or Rmarkdown) for preparing and formatting contributions to the ARTS data set 

![image](https://github.com/whrc/ARTS/blob/main/img/Yang_RTS_site_figure1_Dec_5_2023%20sm.jpg)

## Instructions for Use

### Installation
```
pip install git+https://github.com/whrc/ARTS.git
```
### Steps for contributing to the ARTS data set
**1. Fork this Respository and Clone Your Fork Onto Your Local Machine**

Fork this repository using the **Fork** button in the top right corner in the browser. Next, clone your forked repository. From the forked repository on your github page, copy the URL using the **Code** button in the top right of the browser. From the command line (whichever shell you use for git), navigate to the directory in which you would like to clone the repository (this should be the directory in which you would like to work on this project), and run: `git clone {URL}`.

**2. Set Up a Conda Environment from env.yml**

Make sure you have [Anaconda](https://www.anaconda.com/download/) or [Miniconda](https://docs.conda.io/projects/miniconda/en/latest/) installed. [Mamba](https://anaconda.org/conda-forge/mamba) is also recommended (mamba is not required, but is much faster than conda).

In the command line, make sure you are in the repository directory and run: `mamba env create -f env.yml` (or `conda env create -f env.yml`, if you don't have mamba installed). This will create a conda environment named **rts_dataset**. Run: `conda env list` to ensure that **rts_dataset** shows up.

**3. Run the Scripts (Choose either Rmarkdown or Jupyter Notebook)**

Copy your new, pre-formatted RTS file into the **input_data** folder. Take a look at **input_data/metadata_description** for formatting requirements.
   
If using Python, ensure you are in the repository directory and activate the conda environment by running: `conda activate rts_dataset`. Open **Tutorial/rts_dataset_formatting.ipynb** in either Jupyter Notebook or Jupyter Lab by running: `jupyter notebook` or `jupyter lab`. Follow the instructions in the script to format your data set.
   
If using R, open the project, **rts_dataset.Rproj**, in RStudio. Open **Tutorial/rts_dataset_formatting.Rmd**. Install any missing packages required to run the script. Follow the instructions in the script to format your data set. If you encounter issues during uuid generation, make sure that **rts_dataset** is specified as the python interpreter in the python section of project options (Tools > Project Options > Python).

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


Selected Data Examples
![image](https://github.com/whrc/ARTS/blob/main/img/RTSfigure.jpg)



