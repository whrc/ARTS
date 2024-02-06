# add_empty_columns
add_empty_columns = function(df, column_names) {
  for (name in column_names) {
    if (!name %in% colnames(df)) {
      df = df |>
        mutate(!!!setNames(NA, name))
    }
  }
  return(df)
}

get_unclassified_intersections = function(
    Intersections, 
    SelfIntersections, 
    RepeatRTS, 
    StabilizedRTS,
    NewRTS,
    MergedRTS,
    AccidentalOverlap,
    UnknownRelationship) {
  
  all_intersections = c(
    str_split(Intersections, ',')[[1]],
    str_split(SelfIntersections, ',')[[1]]
    ) |>
    unique()
  all_intersections = all_intersections[which(all_intersections != '')]
  
  all_classifications = c(
    str_split(RepeatRTS, ',')[[1]],
    str_split(StabilizedRTS, ',')[[1]],
    str_split(NewRTS, ',')[[1]],
    str_split(MergedRTS, ',')[[1]],
    str_split(AccidentalOverlap, ',')[[1]],
    str_split(UnknownRelationship, ',')[[1]]
  )
  all_classifications = all_classifications[which(all_classifications != '')]
  
  unclassified_intersections = str_flatten(
    all_intersections[which(!all_intersections %in% all_classifications)],
    ','
    )
  
  return(unclassified_intersections)
  
}

# check_intersection_info
check_intersection_info = function(df, new_data_file, base_dir) {
  
  int_info_complete = df |>
    rowwise() |>
    mutate(
      unclassified_intersections = get_unclassified_intersections(
        Intersections,
        SelfIntersections,
        RepeatRTS, 
        StabilizedRTS,
        NewRTS,
        MergedRTS,
        AccidentalOverlap,
        UnknownRelationship
      )
    ) |>
    ungroup() |>
    mutate(
      int_info_complete = case_when(
        (
          is.na(unclassified_intersections) | str_length(unclassified_intersections)==0
        )  ~ TRUE,
        TRUE ~ FALSE
      )
    )
  
  if (!all(int_info_complete$int_info_complete)) {
    
    incomplete_info = int_info_complete |>
      filter(int_info_complete == FALSE)
    
    st_write(incomplete_info, paste(
      base_dir,
      'output',
      paste0(str_split(new_data_file, '\\.')[[1]][1],
             '_incomplete_information.geojson'),
      sep = '/'), 
      append = FALSE)
    
    print(
      incomplete_info
    )
    
    stop(
      paste0(
        'Incomplete information provided about intersecting RTS polygons. Please complete information for rows printed above. This file has also been saved to ', paste(
          'output',
          paste0(str_split(new_data_file, '\\.')[[1]][1],
                 '_incomplete_information.geojson'),
          sep = '/')),
      ', so that you can determine the problem in your preferred GIS software.'
    )
  }
  
  print('Intersection information is complete.')
  
}

# get_earliest_uid
# Return `UID` from feature with earliest `BaseMapDate` for features in `new_data` that overlap eachother.
get_earliest_uid = function(new_data, uid_col, self_intersections_col) {
  
  indices = c(uid_col,
              split_string_to_vector(self_intersections_col))
  
  indices = indices[!is.na(indices) & indices != '']
  
  id = new_data |>
    filter(UID %in% indices) |>
    mutate(StartDate = ymd(str_split(BaseMapDate, ',')[[1]][1])) |>
    filter(StartDate == min(StartDate)) |>
    pull(UID)
  
  # If there are multiple entries returned, take the first one
  if (length(id) > 1) {
    id = id[1]
  }
  
  return(id)
  
}

# get_uids_by_index_string
get_uids_by_index_string = function(index_string, df) {
  str_flatten(df |>
                slice(as.numeric(
                  str_split(index_string, ',') |>
                    pluck(1))
                ) |>
                pull(UID) |>
                unique(),
              collapse = ',')
}

# remove_adjacent_polys
remove_adjacent_polys = function(intersections, adjacent_polys) {
  intersections = str_split(intersections, ',')
  adjacent_polys = str_split(adjacent_polys, ',')
  
  intersections = map2_chr(intersections,
                        adjacent_polys,
                        ~ str_flatten(.x[which(!.x %in% .y)], collapse = ','))
  
  return(intersections)
  
}

# run_formatting_checks
check_lat = function(lat) {
  
  correct_type = class(lat) == 'numeric'
  missing_values = any(is.na(lat))
  reasonable_values = all(lat >= -90 & lat <= 90)
  
  if (!correct_type) {
    stop('The CentroidLat column is not numeric. Ensure that latitude is reported as decimal degress in WGS 84.')
  } else if (missing_values) {
    stop('The CentroidLat column is missing values.')
  } else if (!reasonable_values) {
    stop('Unexpected values found in the CentroidLat column. Ensure that CentroidLat is listed as decimal degress in WGS 84.')
  }
}

check_lon = function(lon) {
  
  correct_type = class(lon) == 'numeric'
  missing_values = any(is.na(lon))
  reasonable_values = all(lon >= -180 & lon <= 180)
  
  if (!correct_type) {
    stop('The CentroidLon column is not numeric. Ensure that longitude is listed as decimal degress in WGS 84.')
  } else if (missing_values) {
    stop('The CentroidLon column is missing values.')
  } else if (!reasonable_values) {
    stop('Unexpected values found in the CentroidLon column. Ensure that CentroidLon is listed as decimal degress in WGS 84.')
  }
}

check_region = function(region) {
  
  correct_type = class(region) == 'character'
  missing_values = any(is.na(region))
  
  if (!correct_type) {
    stop('The RegionName column is not a string.')
  } else if (missing_values) {
    stop('The RegionName column is missing values.')
  }
}

check_creator = function(creator) {
  
  correct_type = class(creator) == 'character'
  missing_values = any(is.na(creator))
  
  if (!correct_type) {
    stop('The CreatorName column is not a string.')
  } else if (missing_values) {
    stop('The CreatorName column is missing values.')
  }
}

check_basemap_date = function(basemap_date) {
  
  correct_type = all(
    as.logical(
      map(
        basemap_date |>
          str_split(pattern = ','),
        ~ class(
          .x |>
            ymd()
        ) == 'Date'
      )
    )
  )
  missing_values = any(is.na(basemap_date))
  
  if (!correct_type) {
    stop('The BaseMapDate column does not contain dates (or they are improperly formatted).')
  } else if (missing_values) {
    stop('The BaseMapDate column is missing values.')
  }
}

check_source = function(source) {
  
  correct_type = class(source) == 'character'
  missing_values = any(is.na(source))
  
  if (!correct_type) {
    stop('The BaseMapSource column is not a string.')
  } else if (missing_values) {
    stop('The BaseMapSource column is missing values.')
  }
}

check_resolution = function(resolution) {
  
  correct_type = class(resolution) == 'numeric'
  missing_values = any(is.na(resolution))
  
  if (!correct_type) {
    stop('The BaseMapResolution column is not numeric.')
  } else if (missing_values) {
    stop('The BaseMapResolution column is missing values.')
  }
}

check_train_class = function(train_class) {
  
  correct_type = class(train_class) == 'character'
  missing_values = any(is.na(train_class))
  
  if (!correct_type) {
    stop('The TrainClass column is not a string.')
  } else if (missing_values) {
    stop('The TrainClass column is missing values.')
  }
}

check_label_type = function(label_type) {
  
  correct_type = class(label_type) == 'character'
  missing_values = any(is.na(label_type))
  
  if (!correct_type) {
    stop('The TrainClass column is not a string.')
  } else if (missing_values) {
    stop('The TrainClass column is missing values.')
  }
}

run_formatting_checks = function(df) {
  check_lat(df$CentroidLat)
  check_lon(df$CentroidLon)
  check_region(df$RegionName)
  check_creator(df$CreatorLab)
  check_basemap_date(df$BaseMapDate)
  check_source(df$BaseMapSource)
  check_resolution(df$BaseMapResolution)
  check_train_class(df$TrainClass)
  check_label_type(df$LabelType)
  
  print('Formatting looks good!')
}

# split_string_to_vector
split_string_to_vector = function(UID_string) {
  UID_string |>
    str_split(',') |>
    pluck(1)
}

preprocessing = function(
    new_data_filepath,
    required_fields,
    generated_fields,
    optional_fields,
    new_fields,
    calculate_centroid
    ) {
  
  new_data = read_sf(new_data_filepath) |>
    distinct() # remove duplicated rows
  
  # convert to EPSG:3413 if necessary
  if (st_crs(new_data) != st_crs(3413)) {
    new_data = st_transform(new_data, crs = 3413)
  }
  
  # calculate centroid, if requested
  if (calculate_centroid) {
    
    new_data = new_data |>
      select(-any_of(c('CentroidLat', 'CentroidLon'))) |>
      bind_cols(
        st_coordinates(
          st_centroid(
            new_data
          ) |>
            st_transform('EPSG:4326')
        )
      )
    
    if (str_detect(new_data_filepath, '\\.geojson')) {
      new_data = new_data |>
        rename(CentroidLat = Y, CentroidLon = X) |>
        mutate(CentroidLat = round(CentroidLat, 5),
               CentroidLon = round(CentroidLon, 5))
      
    } else if (str_detect(new_data_filepath, '\\.shp')) {
      new_data = new_data |>
        rename(CntrdLt = Y, CntrdLn = X) |>
        mutate(CntrdLt = round(CntrdLt, 5),
               CntrdLn = round(CntrdLn, 5))
      
    }
    
  }
  
  # select correct columns
  if (str_detect(new_data_filepath, '\\.geojson')) {
    
    new_data = new_data |>
      select(
        all_of(c(!!!required_fields)),
        any_of(c(!!!generated_fields)),
        any_of(c(!!!optional_fields)),
        all_of(c(!!!new_fields))
      )
    
  } else if (str_detect(new_data_filepath, '\\.shp')) {
    
    new_data = new_data |>
      select(
        all_of(
          c(!!!setNames(
            c('CntrdLt', 'CntrdLn', 'ReginNm', 'CretrLb', 'BasMpDt', 'BsMpSrc', 'BsMpRsl', 'TrnClss', 'LablTyp'),
            required_fields
          ))
        ),
        any_of(
          c(!!!setNames(
            c('MrgdRTS', 'NewRTS', 'StblRTS', 'UnknwnR', 'ContrDt', 'UID'),
            generated_fields)
          )
        ),
        any_of(
          c(!!!setNames(
            c('BsMpID', 'Area', 'Names'),
            optional_fields)
          )
        ),
        all_of(
          c(!!!setNames(
            new_fields_abbreviated,
            new_fields
          )))
      )
    
  }
  
  return(new_data)
  
}

seed_gen = function(new_data) {
  new_data = new_data |>
    rowwise() |>
    mutate(
      seed = str_flatten(
        c(
          round(CentroidLat, 5),
          round(CentroidLon, 5),
          RegionName,
          CreatorLab,
          BaseMapDate,
          BaseMapSource,
          BaseMapResolution,
          TrainClass,
          LabelType
        )
      ),
      .after = TrainClass
    ) |>
    ungroup()
  
  return(new_data)
}

check_intersections = function(new_data, main_data, out_path, demo) {
  new_data = new_data %>%
    mutate(
      # get indices of polygons in main dataset which overlap or touch
      IntersectionIndices = map_chr(
        st_intersects(new_data,
                      main_data,
                      sparse = TRUE),
        ~ str_flatten(.x, collapse = ',')
      ),
      # get indices of polygons in main dataset with touch, but do not overlap
      AdjacentPolys = map_chr(
        st_touches(new_data,
                   main_data,
                   sparse = TRUE),
        ~ str_flatten(.x, collapse = ',')
      ),
      # remove indices of touching polygons to get polygons which overlap
      IntersectionIndices = remove_adjacent_polys(IntersectionIndices, AdjacentPolys),
      idx = seq(1:nrow(new_data)),
      # get indices of polygons within new dataset which overlap or touch (excluding itself)
      SelfIntersectionIndices = map_chr(
        st_intersects(x = new_data, remove_self = TRUE),
        ~ str_flatten(.x, collapse = ',')
      ),
      # get indices of polygons within new dataset which touch, but do not overlap (excluding self)
      SelfAdjacentPolys = map_chr(
        st_touches(x = new_data, remove_self = TRUE),
        ~ str_flatten(.x, collapse = ',')
      ),
      # remove indices of touching polygons to get polygons which overlap within new dataset
      SelfIntersectionIndices = remove_adjacent_polys(
        SelfIntersectionIndices,
        SelfAdjacentPolys
      ),
      .after = colnames(new_data)[length(which(colnames(new_data) != 'geometry'))]
    ) %>%
    rowwise() %>%
    mutate(
      # convert indices of overlapping polygons to UID
      Intersections = get_uids_by_index_string(IntersectionIndices, main_data),
      SelfIntersections = get_uids_by_index_string(SelfIntersectionIndices, new_data),
      .after = Intersections
    ) %>%
    ungroup() %>%
    select(-c(IntersectionIndices, SelfIntersectionIndices, AdjacentPolys, SelfAdjacentPolys))
  
  overlapping_data = new_data %>%
    filter(str_length(Intersections) > 0 | str_length(SelfIntersections) > 0)
  
  if (nrow(overlapping_data) > 0) {
    
    if (!'RepeatRTS' %in% colnames(overlapping_data)) {
      overlapping_data = overlapping_data %>%
        mutate(RepeatRTS = NA,
               .before = geometry)
    }
    if (!'MergedRTS' %in% colnames(overlapping_data)) {
      overlapping_data = overlapping_data %>%
        mutate(MergedRTS = NA,
               .before = geometry)
    }
    if (!'NewRTS' %in% colnames(overlapping_data)) {
      overlapping_data = overlapping_data %>%
        mutate(NewRTS = NA,
               .before = geometry)
    }
    if (!'StabilizedRTS' %in% colnames(overlapping_data)) {
      overlapping_data = overlapping_data %>%
        mutate(StabilizedRTS = NA,
               .before = geometry)
    }
    
    if (!'AccidentalOverlap' %in% colnames(overlapping_data)) {
      overlapping_data = overlapping_data %>%
        mutate(AccidentalOverlap = NA,
               .before = geometry)
      
    }
   
    if (!'UnknownRelationship' %in% colnames(overlapping_data)) {
      overlapping_data = overlapping_data %>%
        mutate(UnknownRelationship = NA,
               .before = geometry)
      
    }
    
    print(overlapping_data)
    
    if (!demo) {
      
      st_write(overlapping_data,
               out_path, 
               append = FALSE)
      
      print(paste('Overlapping polygons have been saved to', 
                  out_path))
      
    }
   
  } else {
    print('There were no overlapping polygons. Proceed to the next code chunk without any manual editing.')
  }
  
  return(new_data)
  
}

update_uid = function(new_data, uid, repeat_rts, intersections, self_intersections) {
  
  not_repeat = is.na(repeat_rts)
  if (not_repeat) {
    output <- uid
  }
  
  original_uid_exists = any(str_split(repeat_rts, ',')[[1]] %in% str_split(intersections, ',')[[1]])
  
  original_uid = str_split(repeat_rts, ',')[[1]][
    which(str_split(repeat_rts, ',')[[1]] %in% str_split(intersections, ',')[[1]])
    ]
  
  if (original_uid_exists & !not_repeat) {
    output <- original_uid
  }
  
  oldest_new_uid = get_earliest_uid(ungroup(new_data), uid, self_intersections)
  
  if (!original_uid_exists & !not_repeat) {
    output <- oldest_new_uid
  }
  
  return(
    output
  )
}

merge_data = function(new_data, edited_file) {
  
  if (file.exists(edited_file)) {
    
    overlapping_data = read_sf(edited_file)
    
    if ('Area' %in% colnames(overlapping_data)) {
      if (!class(overlapping_data$Area) %in% c('integer', 'numeric')) {
        overlapping_data <- overlapping_data |>
          mutate(Area = as.numeric(Area))
      }
    }
    
    new_data = new_data %>%
      full_join(overlapping_data %>%
                  st_drop_geometry(),
                by = colnames(new_data |>
                                st_drop_geometry())) %>%
      mutate(ContributionDate = format(Sys.time(), '%Y-%m-%d')) %>%
      rowwise() %>%
      mutate(
        UID = update_uid(., UID, RepeatRTS, Intersections, SelfIntersections)
      ) %>%
      select(!matches('geometry')) # doesn't actually remove geometry column, but makes sure it is the last column after the join
    
  } else {
    new_data = new_data %>%
      mutate(RepeatRTS = NA,
             MergedRTS = NA,
             NewRTS = NA,
             StabilizedRTS = NA,
             AccidentalOverlap = NA,
             UnknownRelationship = NA,
             ContributionDate = format(Sys.time(), '%Y-%m-%d'),
             .before = geometry)
    
    warning('No manually edited file has been imported. This is okay if there were no overlapping polygons, but is a problem otherwise.')
  }
  
  return(new_data)
  
}

output = function(
    new_data,
    main_data,
    new_fields,
    all_fields,
    base_dir,
    new_data_file,
    updated_filepath,
    separate_file,
    demo
    ) {
  if (!demo) {
    
    if (separate_file) {
      
      if (!file.exists(
        paste(base_dir, 'output', sep = '/')
      )) {
        dir.create(paste(base_dir, 'output', sep = '/'))
      }
      
      filepath = paste(
        base_dir,
        'output', 
        paste0(
          str_split(new_data_file, '\\.')[[1]][1], 
          '_formatted.geojson'
        ), 
        sep = '/')
      
      st_write(new_data,
               filepath, 
               append = FALSE)
      
    } else {
      
      main_data = main_data |>
        add_empty_columns(
          names(new_fields)
        ) |>
        select(all_of(all_fields))
      
      updated_data = main_data |>
        rbind(new_data)
      
      if (!file.exists(
        updated_filepath
      )) {
        updated_filepath
      }
      
      st_write(updated_data,
               paste(updated_filepath, 'ARTS_main_dataset.geojson', sep = '/'), 
               append = FALSE)
      
      print(updated_filepath)
      
    }
    
  }
  
}