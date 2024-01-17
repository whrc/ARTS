import uuid
import numpy as np
import pandas as pd
import geopandas as gpd
import warnings
import re
from datetime import datetime
from pathlib import Path
import os
from os.path import dirname

# add_empty_columns
def add_empty_columns(df, column_names):
  
  for name in column_names:
    if name not in df.columns:
      df[name] = pd.NA
      
  return df

# check_intersection_info
def check_intersection_info(df):

  duplicated_uids = df['UID'].duplicated()  
  duplicated_uids = df.loc[duplicated_uids, 'UID']
  
  df['int_info_complete'] = (
    (df['Intersections'].isnull()) & (df['SelfIntersectionIndices'].str.len() == 0) |
    (~df['Intersections'].isnull()) & (df['RepeatRTS'].notnull() | df['MergedRTS'].notnull() | df['StabilizedRTS'].notnull() | df['AccidentalOverlap'].notnull()) | 
    (df['SelfIntersectionIndices'].str.len() > 0) & (df['UID'].isin(duplicated_uids))
  )
  
  if not df['int_info_complete'].all():
    print(df[~df['int_info_complete']])
    raise Exception('Incomplete intersection information provided. See printed rows.')
  
  print('Intersection information is complete.')

# get_earliest_uid
# Return `UID` from feature with earliest `BaseMapDate` for features in `new_data` that overlap eachother.
def get_earliest_uid(df_subset, df):

    uids = [df_subset['UID']] + [x for x in df_subset['SelfIntersectionIndices'].split(',')]
     
    df = df[df.UID.isin(uids)]
    
    earliest_df = df[df.ContributionDate == df.ContributionDate.min()]
    earliest_df = df[df.BaseMapDate == df.BaseMapDate.min()]
    
    return earliest_df.UID.iloc[0]

# get_intersecting_uuids
# this is to get the uuids of any rts polygons which touch or overlap
def get_intersecting_uids(polygon, df):
    intersections = [','.join(gpd.overlay(polygon, df, how='intersection').UID_2)]
    return intersections

# get_touching_uuids
# this is to get the uuids of any rts polygons which touch (only the edges touch, no overlap)
def get_touching_uids(polygon, df):
    adjacent_polys = [','.join([uid for rts, uid in zip(df.geometry, df.UID) if polygon.geometry.touches(rts).reset_index()[0][0]])]
    return adjacent_polys

# remove_adjacent_polys
# this removes the uuids of any polygons which touch, but do not overlap, the current rts polygon from the adjacent_polys column
def remove_adjacent_polys(intersections, adjacent_polys):
    intersections = [item.split(',') for item in intersections]
    adjacent_polys = [item.split(',') for item in adjacent_polys]
    fixed_intersections = []
    for idx in range(0, len(intersections)):
        fixed_intersection = [[intersection for intersection in intersections[idx] if intersection not in adjacent_polys[idx]]]
        fixed_intersections = fixed_intersections + fixed_intersection
    fixed_intersections = [','.join(item) for item in fixed_intersections]
    return fixed_intersections

# run_formatting_checks
def check_lat(lat):
    correct_type = type(lat[0]) == np.float64
    missing_values = pd.isna(lat).values.any()
    reasonable_values = np.all(lat.between(-90, 90))

    if not correct_type:
        raise ValueError('The CentroidLat column is not numeric. Ensure that latitude is reported as decimal degress in WGS 84.')
    elif missing_values:
        raise ValueError('The CentroidLat column is missing values.')
    elif not reasonable_values:
        raise ValueError('Unexpected values found in the CentroidLat column. Ensure that CentroidLat is listed as decimal degress in WGS 84.')

def check_lon(lon):
    correct_type = type(lon[0]) == np.float64
    missing_values = pd.isna(lon).values.any()
    reasonable_values = np.all(lon.between(-180, 180))

    if not correct_type:
        raise ValueError('The CentroidLon column is not numeric. Ensure that longitude is reported as decimal degress in WGS 84.')
    elif missing_values:
        raise ValueError('The CentroidLon column is missing values.')
    elif not reasonable_values:
        raise ValueError('Unexpected values found in the CentroidLon column. Ensure that longitude is listed as decimal degress in WGS 84.')

def check_region(region):
    correct_type = type(region[0]) == str
    missing_values = (region == '').values.any()

    if not correct_type:
        raise ValueError('The RegionName column is not a string.')
    elif missing_values:
        raise ValueError('The RegionName column is missing values.')

def check_creator(creator):
    correct_type = type(creator[0]) == str
    missing_values = (creator == '').values.any()

    if not correct_type:
        raise ValueError('The CreatorLab column is not a string.')
    elif missing_values:
        raise ValueError('The CreatorLab column is missing values.')

def check_basemap_date(basemap_date):
    correct_type = pd.Series([
        type(pd.to_datetime(row)) == pd.core.indexes.datetimes.DatetimeIndex 
         for row in basemap_date.str.split(',')
    ]).values.all()
    missing_values = ((basemap_date.str.split(',', expand = True)).iloc[:, 0] == '').any()

    if not correct_type:
        raise ValueError('The BaseMapDate column does not contain dates (or they are improperly formatted).')
    elif missing_values:
        raise ValueError('The BaseMapDate column is missing values.')
  
def check_source(source):
    correct_type = type(source[0]) == str
    missing_values = (source == '').values.any()

    if not correct_type:
        raise ValueError('The BaseMapSource column is not a string.')
    elif missing_values:
        raise ValueError('The BaseMapSource column is missing values.')

def check_resolution(resolution):
    correct_type = type(resolution[0]) == np.float64
    missing_values = pd.isna(resolution).values.any()

    if not correct_type:
        raise ValueError('The BaseMapResolution column is not a numeric.')
    elif missing_values:
        raise ValueError('The BaseMapResolution column is missing values.')

def check_train_class(train_class):
    correct_type = type(train_class[0]) == str
    missing_values = (train_class == '').values.any()

    if not correct_type:
        raise ValueError('The TrainClass column is not a string.')
    elif missing_values:
        raise ValueError('The TrainClass column is missing values.')

def run_formatting_checks(df):
    check_lat(df.CentroidLat)
    check_lon(df.CentroidLon)
    check_region(df.RegionName)
    check_creator(df.CreatorLab)
    check_basemap_date(df.BaseMapDate)
    check_source(df.BaseMapSource)
    check_resolution(df.BaseMapResolution)
    check_train_class(df.TrainClass)
    
    print('Formatting looks good!')
    
    
def preprocessing(your_rts_dataset_dir, required_fields, optional_fields, new_fields, calculate_centroid):
    
    new_data = gpd.read_file(your_rts_dataset_dir)
    new_data_filepath = your_rts_dataset_dir

    if new_data.crs != 'EPSG:3413':
        new_data = new_data.to_crs('EPSG:3413')

    if calculate_centroid:
        if re.search('\\.shp', str(new_data_filepath)):
            new_data = new_data.drop(['CntrdLt', 'CntrdLn'], axis = 1)
            
        new_data["CentroidLat"] = new_data.to_crs(4326).centroid.y
        new_data["CentroidLon"] = new_data.to_crs(4326).centroid.x

    if re.search('\\.geojson', str(new_data_filepath)):
        new_data = (
            new_data    
            .filter(items = required_fields + optional_fields + new_fields + ['geometry'])
            )
    elif re.search('\\.shp', str(new_data_filepath)):
        new_data = (
            new_data    
            .rename(columns = dict(
                {key:value for key, value 
                    in zip(
                        ['CntrdLt', 'CntrdLn', 'ReginNm', 'CretrLb', 'BasMpDt', 'BsMpSrc', 'BsMpRsl', 'TrnClss'], 
                        [item for item in required_fields if item not in ['MergedRTS', 'StabilizedRTS', 'UID', 'ContributionDate']]
                    )},
                    **{key:value for key, value 
                    in zip(
                        ['StblRTS', 'MrgdRTS', 'Area'], 
                        [item for item in optional_fields if item not in ['MergedRTS', 'StabilizedRTS', 'UID', 'ContributionDate']],
                    )},
                    **{key:value for key, value 
                in zip(
                    new_fields_abbreviated,   # Heidi : this is not defined, please fix
                    new_fields)}
                )
                    )
            .filter(items = required_fields + optional_fields + new_fields + ['geometry'])
            )

    for field in [item for item in required_fields if item not in ['MergedRTS', 'StabilizedRTS', 'UID', 'ContributionDate']]: # Check if all required columns are present
        if field not in new_data.columns:
            raise ValueError('{field} is missing. Ensure that all required fields (except UID) are present prior to running this script'
                            .format(field = repr(field)))

    for field in [item for item in new_fields]: # Check if all new columns are present
        if field not in new_data.columns:
            raise ValueError('{field} is missing. Did you specify the name of the new metadata field correctly?'.format(field = repr(field)))

    return new_data





def check_intersections(processed_data, your_rts_dataset_dir, ARTS_main_dataset):
    new_data = processed_data

    intersections = []
    for idx in range(0,new_data.shape[0]):
        new_intersections = get_intersecting_uids(new_data.iloc[[idx]], ARTS_main_dataset)
        intersections = intersections + new_intersections
        
    new_data['Intersections'] = intersections

    adjacent_polys = []
    for idx in range(0,new_data.shape[0]):
        new_adjacent_polys = get_touching_uids(new_data.iloc[[idx]], ARTS_main_dataset)
        adjacent_polys = adjacent_polys + new_adjacent_polys
        
    new_data['AdjacentPolys'] = adjacent_polys

    new_data.Intersections = remove_adjacent_polys(new_data.Intersections, new_data.AdjacentPolys)
    new_data.drop('AdjacentPolys', axis=1)

    overlapping_data = new_data.copy()
    overlapping_data = overlapping_data[overlapping_data.Intersections.str.len() > 0]

    if overlapping_data.shape[0] > 0:
        if 'RepeatRTS' not in list(overlapping_data.columns.values):
            overlapping_data['RepeatRTS'] = ['']*overlapping_data.shape[0]
        if 'MergedRTS' not in list(overlapping_data.columns.values):
            overlapping_data['MergedRTS'] = ['']*overlapping_data.shape[0]
        if 'StabilizedRTS' not in list(overlapping_data.columns.values):
            overlapping_data['StabilizedRTS'] = ['']*overlapping_data.shape[0]

        overlapping_data['AccidentalOverlap'] = ['']*overlapping_data.shape[0]

        print(overlapping_data)

        with open('overlapping_polygons.geojson', 'w') as f: # provide your path here
          f.write(overlapping_data.to_json())

    else:
        print('There were no overlapping polygons. Proceed to the next code chunk without any manual editing.')
    return


def merge_data(edited_file_path,processed_data):
    edited_file = Path(edited_file_path)
    if Path.exists(edited_file):
        overlapping_data = (
            gpd.read_file(edited_file)
            .filter(items = ['UID', 'Intersections', 'RepeatRTS', 'MergedRTS', 'StabilizedRTS', 'AccidentalOverlap'])
            )

        merged_data = pd.merge(processed_data,
                            overlapping_data,
                            how = 'outer',
                            on = ['UID', 'Intersections'])

        merged_data.loc[~merged_data.RepeatRTS.isnull(), 'UID'] = merged_data.RepeatRTS[~merged_data.RepeatRTS.isnull()]

    else:
        merged_data['RepeatRTS'] = ['']*processed_data.shape[0]
        merged_data['MergedRTS'] = ['']*processed_data.shape[0]
        merged_data['StabilizedRTS'] = ['']*processed_data.shape[0]
        merged_data['AccidentalOverlap'] = ['']*processed_data.shape[0]

        warnings.warn("No manually edited file has been imported. This is okay if there were no overlapping polygons, but is a problem otherwise.")
    return merged_data

def seed_gen(gpd):
    gpd['seed'] = (gpd[[
                        'CentroidLat',
                        'CentroidLon',
                        'RegionName',
                        'CreatorLab',
                        'BaseMapDate',
                        'BaseMapSource',
                        'BaseMapResolutionStr',
                        'TrainClass',
                        'LabelType'
                    ]].apply(
                        lambda row: ''.join(row.values.astype(str)),
                        axis = 1
                    ))
    return gpd