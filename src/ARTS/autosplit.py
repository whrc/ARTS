import numpy as np
import pandas as pd
import geopandas as gpd
import math
import random


def split_with_buffer(df, subset_names, probs, tile_size):
    """
     Split a dataframe into subsets. This is useful for leakage-free data splitting for deep learning model training.
     @param df - The dataframe to be split. It must have the'zone'and'buffer'columns
     @param subset_names - The names of the training subset
     @param probs
     @param tile_size
    """

    if len(subset_names) != len(probs):
        raise ValueError(
            "The length of subset_names must be equal to the length of probs.")

    # buffer polygons with information from tile_size
    df_buffer = df
    # may be able to change this to be more conservative, depending on how tiles are centered on polygons
    df_buffer['buffer'] = df.buffer(math.sqrt(tile_size**2 * 2))
    df_buffer = df_buffer.set_geometry('buffer')
    df_buffer['zone'] = 0

    # find groups of polygons that are close together and must be kept in the same training subset
    grouped_df = df_buffer[['zone', 'buffer']].dissolve(
        by='zone').explode(ignore_index=True)

    # get the count of polygons in each group
    grouped_df['count'] = df_buffer.sjoin(
        grouped_df).groupby(['index_right'])['ID'].count()

    # Arrange by number of polygons within each group; starting with large groups and finishing with small groups makes it more likely that you actually get the desired number of polygons in each group
    grouped_df = grouped_df.sort_values(
        by='count', ascending=False, ignore_index=True)

    # prep variables to keep track of how many polygons are in each subset throughout the subset assignment for loop
    # could be off by 1 row due to rounding
    target_n = [round(value*df.shape[0]) for value in probs]

    # fix potential rounding error - is there a more concise way to add one to the element of target_n which has the largest decimal place value?
    if df.shape[0] - sum(target_n) == 1:
        weighted = [value*df.shape[0] for value in [0.8, 0.1, 0.1]]
        mod = [value % 1 for value in weighted]
        idx = [idx for idx, value in enumerate(mod) if value == max(mod)]
        target_n[idx[0]] = target_n[idx[0]] + 1

    counts = [0]*len(subset_names)

    probs = dict(zip(subset_names, probs))
    target_n = dict(zip(subset_names, target_n))
    counts = dict(zip(subset_names, counts))

    # assign subset groups to polygons in for loop
    subsets = []
    for idx, row in grouped_df.iterrows():

        # check if any categories have been completed and remove those categories from what can be assigned as a subset group
        complete_categories = [
            key for key in target_n if counts[key] == target_n[key]]
        subset_names = [
            item for item in subset_names if item not in complete_categories]
        probs = {key: prob for key, prob in probs.items(
        ) if key not in complete_categories}
        probs = {key: prob/sum(probs.values()) for key, prob in probs.items()}

        # randomly choose a subset group
        subset = random.choices(subset_names, weights=list(probs.values()))[0]

        # check if applying the new subset group to the next row will overshoot the target number for that group
        if idx < grouped_df.shape[0] and counts[subset] + grouped_df['count'].iloc[idx] > target_n[subset]:
            skip_subset = [subset]

            subset = random.choices(
                [key for key in subset_names if key != skip_subset],
                weights=[prob/sum([prob for key, prob in probs.items() if key != skip_subset])
                         for key, prob in probs.items() if key != skip_subset]

            )[0]

        if idx < grouped_df.shape[0] and counts[subset] + grouped_df.iloc[idx]['count'] > target_n[subset]:
            skip_subset = skip_subset + [subset]

            subset = random.choices(
                [key for key in subset_names if key != skip_subset],
                weights=[prob/sum([prob for key, prob in probs.items() if key != skip_subset])
                         for key, prob in probs.items() if key != skip_subset]

            )[0]

        counts[subset] = counts[subset] + grouped_df['count'].iloc[idx]

        subsets = subsets + [subset]

    grouped_df['subset'] = subsets
    groups_df = df_buffer.sjoin(
        grouped_df)[['ID', 'Long', 'Lat', 'subset', 'geometry']]
    groups_df = groups_df.set_geometry('geometry')

    return groups_df
