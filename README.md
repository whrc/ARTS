# ARTS
The Arctic Retrogressive Thaw Slumps Data Set

![image](https://github.com/whrc/ARTS/blob/main/img/Yang_RTS_site_figure1_Dec_5_2023%20sm.jpg)


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
