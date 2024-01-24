import numpy as np
import pandas as pd
import geopandas as gpd
import warnings
import re
from datetime import datetime
from pathlib import Path


def add_empty_columns(df, column_names):
    """
    Adds columns filled with NA values to a dataframe.
    This ensures that all optional metadata columns are present in the output dataset.

    @param df - DataFrame to add columns to
    @param column_names - List of column names to add to the DataFrame

    @return DataFrame with columns added to it
    """
    for name in column_names:
        if name not in df.columns:
            df[name] = pd.NA

    return df


def check_intersection_info(df):
    """
     Checks that intersection information has been completed for every polygon.
     If there is an intersection reported in any row and the UID of that intersection has not been placed
     into one of "RepeatRTS", "MergedRTS", "StabilizedRTS", or "AccidentalOverlap", the test fails.

     @param df - Dataframe containing information about RTS intersections and self - intersections.
    """

    duplicated_uids = df['UID'].duplicated()
    duplicated_uids = df.loc[duplicated_uids, 'UID']

    df['int_info_complete'] = (
        (df['Intersections'].isnull()) & (df['SelfIntersectionIndices'].str.len() == 0) |
        (~df['Intersections'].isnull()) & (df['RepeatRTS'].notnull() | df['MergedRTS'].notnull() | df['StabilizedRTS'].notnull() | df['AccidentalOverlap'].notnull()) |
        (df['SelfIntersectionIndices'].str.len() > 0) & (
            df['UID'].isin(duplicated_uids))
    )

    if not df['int_info_complete'].all():
        print(df[~new_data['int_info_complete']])
        raise Exception(
            'Incomplete intersection information provided. See printed rows.')

    print('Intersection information is complete.')


def get_earliest_uid(polygon, new_data):
    '''
    get_earliest_uid
    Gets the UID of the first version of an RTS which was contributed to the dataset. If there are multiple versions of the same RTS within the same contribution, the feature with the earliest base map date is used.

    @param polygon - A geodataframe with a single RTS feature.
    @param new_data - The main ARTS data set.

    @return `UID` from feature with earliest `ContributionDate` and `BaseMapDate` for features in `new_data` that overlap eachother.
    '''
    uids = [polygon['UID']] + \
        [x for x in polygon['SelfIntersectionIndices'].split(',')]

    new_data = new_data[new_data.UID.isin(uids)]

    earliest = new_data[new_data.ContributionDate == new_data.ContributionDate.min()]
    earliest = earliest[new_data.BaseMapDate == new_data.BaseMapDate.min()]

    return earliest.UID.iloc[0]


def get_intersecting_uids(polygon, main_data):
    '''
    get_intersecting_uuids
    Gets the UIDs of any RTS polygons which overlap or touch.

    @param polygon - A geodataframe with a single RTS feature.
    @param main_data - The main ARTS data set.

    @return `UID` of overlapping or touching RTS.
    '''
    intersections = [','.join(gpd.overlay(
        polygon, main_data, how='intersection').UID_2)]
    return intersections


def get_touching_uids(polygon, main_data):
    '''
    get_touching_uuids
    Gets the UIDs of any rts polygons which touch (only the edges touch, no overlap)

    @param polygon - A geodataframe with a single RTS feature.
    @param main_data - The main ARTS data set.

    @return `UID` of touching RTS.
    '''
    adjacent_polys = [','.join([uid for rts, uid in zip(
        main_data.geometry, main_data.UID) if polygon.geometry.touches(rts).reset_index()[0][0]])]
    return adjacent_polys


def remove_adjacent_polys(intersections, adjacent_polys):
    '''
    remove_adjacent_polys
    Removes the UIDs from the adjacent_polys column of any polygons which touch, but do not overlap, the current rts polygon.

    @param intersections - The column of the new data which contains UIDs of intersecting RTS.
    @param adjacent_polys - The column of the new data which contains UIDs of adjacent RTS.

    @return `UID` of overlapping (but not touching) RTS.
    '''
    intersections = [item.split(',') for item in intersections]
    adjacent_polys = [item.split(',') for item in adjacent_polys]
    fixed_intersections = []
    for idx in range(0, len(intersections)):
        fixed_intersection = [
            [intersection for intersection in intersections[idx] if intersection not in adjacent_polys[idx]]]
        fixed_intersections = fixed_intersections + fixed_intersection
    fixed_intersections = [','.join(item) for item in fixed_intersections]
    return fixed_intersections


def check_lat(lat):
    '''
    Checks that latitude values are floats, are not missing, and are between -90 and 90.

    @param lat - The column which contains centroid latitudes.
    '''
    correct_type = type(lat[0]) == np.float64
    missing_values = pd.isna(lat).values.any()
    reasonable_values = np.all(lat.between(-90, 90))

    if not correct_type:
        raise ValueError(
            'The CentroidLat column is not numeric. Ensure that latitude is reported as decimal degress in WGS 84.')
    elif missing_values:
        raise ValueError('The CentroidLat column is missing values.')
    elif not reasonable_values:
        raise ValueError(
            'Unexpected values found in the CentroidLat column. Ensure that CentroidLat is listed as decimal degress in WGS 84.')


def check_lon(lon):
    '''
    Checks that longitude values are floats, are not missing, and are between -180 and 180.

    @param lon - The column which contains centroid longitudes.
    '''
    correct_type = type(lon[0]) == np.float64
    missing_values = pd.isna(lon).values.any()
    reasonable_values = np.all(lon.between(-180, 180))

    if not correct_type:
        raise ValueError(
            'The CentroidLon column is not numeric. Ensure that longitude is reported as decimal degress in WGS 84.')
    elif missing_values:
        raise ValueError('The CentroidLon column is missing values.')
    elif not reasonable_values:
        raise ValueError(
            'Unexpected values found in the CentroidLon column. Ensure that longitude is listed as decimal degress in WGS 84.')


def check_region(region):
    '''
    Checks that a region has been supplied as a string.

    @param region - The column that contains the region name.
    '''
    correct_type = type(region[0]) == str
    missing_values = (region == '').values.any()

    if not correct_type:
        raise ValueError('The RegionName column is not a string.')
    elif missing_values:
        raise ValueError('The RegionName column is missing values.')


def check_creator(creator):
    '''
    Checks that a creator has been supplied as a string.

    @param creator - The column that contains the creator lab.
    '''

    correct_type = type(creator[0]) == str
    missing_values = (creator == '').values.any()

    if not correct_type:
        raise ValueError('The CreatorLab column is not a string.')
    elif missing_values:
        raise ValueError('The CreatorLab column is missing values.')


def check_basemap_date(basemap_date):
    '''
    Checks that basemap date formats are a string composed of one or two dates separated by a comma.

    @param basemap_date - The column that contains the base map date.
    '''

    correct_type = pd.Series([
        type(pd.to_datetime(row)) == pd.core.indexes.datetimes.DatetimeIndex
        for row in basemap_date.str.split(',')
    ]).values.all()
    missing_values = ((basemap_date.str.split(
        ',', expand=True)).iloc[:, 0] == '').any()

    if not correct_type:
        raise ValueError(
            'The BaseMapDate column does not contain dates (or they are improperly formatted).')
    elif missing_values:
        raise ValueError('The BaseMapDate column is missing values.')


def check_source(source):
    '''
    Checks that basemap source has been provided as a string.

    @param source - The column that contains the base map source.
    '''

    correct_type = type(source[0]) == str
    missing_values = (source == '').values.any()

    if not correct_type:
        raise ValueError('The BaseMapSource column is not a string.')
    elif missing_values:
        raise ValueError('The BaseMapSource column is missing values.')


def check_resolution(resolution):
    '''
    Checks that resolution has been provided as a float.

    @param resolution - The column that contains the base map resolution.
    '''

    correct_type = type(resolution[0]) == np.float64
    missing_values = pd.isna(resolution).values.any()

    if not correct_type:
        raise ValueError('The BaseMapResolution column is not a numeric.')
    elif missing_values:
        raise ValueError('The BaseMapResolution column is missing values.')


def check_train_class(train_class):
    '''
    Checks that training class has been provided as a string.

    @param train_class - The column that contains the training class.
    '''
    correct_type = type(train_class[0]) == str
    missing_values = (train_class == '').values.any()

    if not correct_type:
        raise ValueError('The TrainClass column is not a string.')
    elif missing_values:
        raise ValueError('The TrainClass column is missing values.')


def check_label_type(label_type):
    '''
    Checks that label type has been provided as a string.
    '''
    correct_type = type(label_type[0]) == str
    missing_values = (label_type == '').values.any()

    if not correct_type:
        raise ValueError('The LabelType column is not a string.')
    elif missing_values:
        raise ValueError('The LabelType column is missing values.')


def run_formatting_checks(df):
    '''
    Checks the format of the metadata columns.

    @param df - The new data set.
    '''
    check_lat(df.CentroidLat)
    check_lon(df.CentroidLon)
    check_region(df.RegionName)
    check_creator(df.CreatorLab)
    check_basemap_date(df.BaseMapDate)
    check_source(df.BaseMapSource)
    check_resolution(df.BaseMapResolution)
    check_train_class(df.TrainClass)
    check_label_type(df.LabelType)

    print('Formatting looks good!')


def preprocessing(new_data_filepath, required_fields, generated_fields, optional_fields, new_fields, calculate_centroid):
    '''
    Reads the RTS data set to be processed, ensures it is in the correct CRS, calculates centroids if requested, filters the columns and checks that all required columns are present.

    @param new_data_filepath - The file path of the new data that needs to be formatted.
    @param required_fields - A list of required metadata columns.
    @param generated_fields - A list of metadata columns that will be created during file formatting.
    @param new_fields - A list of new metadata columns in the new data that should be published in the ARTS data set but have never been included before.
    @param calculate_centroid - Boolean. Should the centroid of each RTS be calculated?

    @return pre-processed geopandas dataframe
    '''
    new_data = gpd.read_file(new_data_filepath)

    # convert to EPSG:3413 if necessary
    if new_data.crs != 'EPSG:3413':
        new_data = new_data.to_crs('EPSG:3413')

    # calculate centroid, if requested
    if calculate_centroid:
        if re.search('\\.shp', str(new_data_filepath)):
            new_data = new_data.drop(['CntrdLt', 'CntrdLn'], axis=1)
            new_data["CntrdLt"] = new_data.to_crs(4326).centroid.y.round(5)
            new_data["CntrdLn"] = new_data.to_crs(4326).centroid.x.round(5)

        elif re.search('\\.geojson', str(new_data_filepath)):
            new_data["CentroidLat"] = new_data.to_crs(4326).centroid.y.round(5)
            new_data["CentroidLon"] = new_data.to_crs(4326).centroid.x.round(5)

    # select correct columns
    if re.search('\\.geojson', str(new_data_filepath)):
        new_data = (
            new_data
            .filter(items=required_fields + generated_fields + optional_fields + new_fields + ['geometry'])
        )
    elif re.search('\\.shp', str(new_data_filepath)):
        new_data = (
            new_data
            .rename(columns=dict(
                {key: value for key, value
                    in zip(
                        ['CntrdLt', 'CntrdLn', 'ReginNm', 'CretrLb', 'BasMpDt',
                            'BsMpSrc', 'BsMpRsl', 'TrnClss', 'LablTyp'],
                        required_fields
                    )},
                **{key: value for key, value
                   in zip(
                       ['MrgdRTS', 'StblRTS', 'ContrDt', 'UID'],
                       generated_fields,
                   )},
                **{key: value for key, value
                   in zip(
                       ['BsMpID', 'Area'],
                       optional_fields,
                   )},
                **{key: value for key, value
                   in zip(
                       new_fields_abbreviated,
                       new_fields
                   )}
            )
            )
            .filter(items=required_fields + optional_fields + new_fields + ['geometry'])
        )

    # Check if all required columns are present
    for field in [item for item in required_fields]:
        if field not in new_data.columns:
            raise ValueError('{field} is missing. Ensure that all required fields are present prior to running this script'
                             .format(field=repr(field)))

    for field in [item for item in new_fields]:  # Check if all new columns are present
        if field not in new_data.columns:
            raise ValueError(
                '{field} is missing. Did you specify the name of the new metadata field correctly?'.format(field=repr(field)))

    return new_data


def check_intersections(new_data, main_data, out_path, demo):
    '''
    Check intersections between data to be submitted and the main data set.

    @param new_data - The new RTS data set.
    @param main_data - The main RTS data set.
    @param out_path - The file path where you would like to save the intersecting polygon data set.
    @param demo - Boolean. Are you running this script as a demo? 

    @return geopandas dataframe with intersecting features
    '''
    intersections = []

    for idx in range(0, new_data.shape[0]):
        new_intersections = get_intersecting_uids(
            new_data.iloc[[idx]], main_data)
        intersections = intersections + new_intersections

    new_data['Intersections'] = intersections

    adjacent_polys = []
    for idx in range(0, new_data.shape[0]):
        new_adjacent_polys = get_touching_uids(new_data.iloc[[idx]], main_data)
        adjacent_polys = adjacent_polys + new_adjacent_polys

    new_data['AdjacentPolys'] = adjacent_polys

    new_data.Intersections = remove_adjacent_polys(
        new_data.Intersections, new_data.AdjacentPolys)
    new_data.drop('AdjacentPolys', axis=1)

    overlapping_data = new_data.copy()
    overlapping_data = overlapping_data[overlapping_data.Intersections.str.len(
    ) > 0]

    if overlapping_data.shape[0] > 0:
        if 'RepeatRTS' not in list(overlapping_data.columns.values):
            overlapping_data['RepeatRTS'] = ['']*overlapping_data.shape[0]
        if 'MergedRTS' not in list(overlapping_data.columns.values):
            overlapping_data['MergedRTS'] = ['']*overlapping_data.shape[0]
        if 'StabilizedRTS' not in list(overlapping_data.columns.values):
            overlapping_data['StabilizedRTS'] = ['']*overlapping_data.shape[0]
        if 'AccidentalOverlap' not in list(overlapping_data.columns.values):
            overlapping_data['AccidentalOverlap'] = ['']*overlapping_data.shape[0]

        print(overlapping_data)

        if demo == False:
            overlapping_data.to_file(
                out_path
            )

            print(
                'Overlapping polygons have been saved to ' +
                str(out_path)
            )

    else:
        print('There were no overlapping polygons. Proceed to the next code chunk without any manual editing.')

    return new_data


def merge_data(new_data, edited_file):
    '''
    merge the data to be submitted with manually edited, intersection-checked file.

    @param new_data - The new data set.
    @param edited_file - The manually edited file with intersection information.

    @return new data with edited columns appended
    '''
    if Path.exists(Path(edited_file)):
        overlapping_data = (
            gpd.read_file(edited_file)
            .filter(items=['UID', 'Intersections', 'RepeatRTS', 'MergedRTS', 'StabilizedRTS', 'AccidentalOverlap'])
        )

        new_data = pd.merge(new_data,
                            overlapping_data,
                            how='outer',
                            on=['UID', 'Intersections'])

        new_data.loc[~new_data.RepeatRTS.isnull(
        ), 'UID'] = new_data.RepeatRTS[~new_data.RepeatRTS.isnull()]

    else:
        new_data['RepeatRTS'] = ['']*new_data.shape[0]
        new_data['MergedRTS'] = ['']*new_data.shape[0]
        new_data['StabilizedRTS'] = ['']*new_data.shape[0]
        new_data['AccidentalOverlap'] = ['']*new_data.shape[0]

        warnings.warn(
            "No manually edited file has been imported. This is okay if there were no overlapping polygons, but is a problem otherwise.")

    return new_data


def seed_gen(new_data):
    '''
    Generate seeds for each row in a geopandas dataframe by concantenating all required fields as str
    The seed is used for UID generation

    @param new_data - The new RTS data set.

    @return New dataframe with a new column 'seed' for UID generation
    '''

    new_data.CentroidLat = np.round(new_data.CentroidLat, 5)
    new_data.CentroidLon = np.round(new_data.CentroidLon, 5)
    c = new_data.BaseMapResolution == new_data.BaseMapResolution.astype(int)
    new_data.loc[c, 'BaseMapResolutionStr'] = new_data.BaseMapResolution.astype(
        int).astype(str)
    new_data.loc[~c, 'BaseMapResolutionStr'] = new_data.BaseMapResolution.astype(
        str)
    new_data['seed'] = (new_data[[
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
        axis=1
    ))
    return new_data


def self_intersection(new_data):
    '''
    Check intersection within a geopandas dataframe

    @param new_data - The new RTS data set.

    @return a dataframe with a column for self-intersections added
    '''

    new_data["ContributionDate"] = datetime.today().strftime('%Y-%m-%d')

    intersections = []
    for idx in range(0, new_data.shape[0]):
        new_intersections = get_intersecting_uids(
            new_data.iloc[[idx]], new_data.drop([idx]))
        intersections = intersections + new_intersections

    new_data['SelfIntersectionIndices'] = intersections

    adjacent_polys = []
    for idx in range(0, new_data.shape[0]):
        new_adjacent_polys = get_touching_uids(
            new_data.iloc[[idx]], new_data.drop(idx))
        adjacent_polys = adjacent_polys + new_adjacent_polys

    new_data['AdjacentPolys'] = adjacent_polys

    new_data.Intersections = remove_adjacent_polys(
        new_data.Intersections, new_data.AdjacentPolys)
    new_data.drop('AdjacentPolys', axis=1)

    new_data.loc[new_data.SelfIntersectionIndices.str.len() > 0, 'UID'] = (
        new_data[new_data.SelfIntersectionIndices.str.len() > 0]
        .apply(get_earliest_uid, new_data=new_data, axis=1)
    )

    return new_data


def output(new_data, main_data, optional_fields, all_fields, base_dir, new_data_file, main_filepath, separate_file, demo):
    '''
    select the desired fields and save the geopandas dataframe to file

    @param new_data - The new RTS data set.
    @param main_data - The main ARTS data set.
    @param optional_fields - A list of optional metadata fields.
    @param all_fields - A list of all the metadata fields to be included in output.
    @param base_dir - The base directory in which to save the output.
    @param new_data_file - The file name of the new RTS dataset.
    @param main_filepath - The file name of the main ARTS dataset.
    @param demo - Boolean. Are you running this script as a demo? 
'''

    if demo == False:

        if separate_file:

            filepath = base_dir / 'python_output' / (
                str(new_data_file).split('.', maxsplit=1)[
                    0] + "_formatted.geojson"
            )

            new_data.to_file(filepath)
            print(str(filepath))

        else:

            main_data = add_empty_columns(
                main_data,
                [col for col in optional_fields]
            )
            main_data.ContributionDate = [value.strftime(
                '%Y-%m-%d') for value in main_data.ContributionDate]

            main_data = main_data[all_fields + ['geometry']]
            updated_data = pd.concat([main_data, new_data])
            updated_data.to_file(main_filepath)
            print(str(main_filepath))
