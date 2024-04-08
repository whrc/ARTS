base_dir = '../ARTS_main_dataset/v.0.0.12-alpha/'
main = st_read("C:/Users/jdean/Documents/GitHub/ARTS/ARTS_main_dataset/v.2.0.0/ARTS_main_dataset.geojson")
main = slice(main, 2:n())

st_write(main, "C:/Users/jdean/Documents/GitHub/ARTS/ARTS_main_dataset/v.2.0.0/ARTS_main_dataset.geojson")

#Add column SplitRTS after Merged ARTS in main dataset
main = st_read("C:/Users/jdean/Documents/GitHub/ARTS/ARTS_main_dataset/v.6.0.0/ARTS_main_dataset_nosplit.geojson")
main$SplitRTS = NA
#reorder to put splitRTS column in between merged and newRTS
main = main[ , c("CentroidLat", "CentroidLon", "RegionName", "CreatorLab","BaseMapDate", "BaseMapSource", "BaseMapResolution","TrainClass", "LabelType", "MergedRTS","SplitRTS","NewRTS","StabilizedRTS","UnknownRelationship", "ContributionDate","UID","BaseMapID", "Area","Notes","geometry")]
st_write(main, "C:/Users/jdean/Documents/GitHub/ARTS/ARTS_main_dataset/v.6.0.0/ARTS_main_dataset.geojson")


#explore main 15 to check whats going on with the points vs polygons 
main15 = st_read("C:/Users/jdean/Documents/GitHub/ARTS/ARTS_main_dataset/v.15.0.0/ARTS_main_dataset.geojson")

main16 = st_read("C:/Users/jdean/Documents/GitHub/ARTS/ARTS_main_dataset/v.16.0.0/ARTS_main_dataset.geojson")


#remove the 40 or so duplicate ids from Banks 2 addition to the main ARTS dataset
main17 = st_read("C:/Users/jdean/Documents/GitHub/ARTS/ARTS_main_dataset/v.17.0.0/ARTS_main_dataset_duplicates.geojson")

#manually remove rows
# Manually identify rows based on column "ID"
id_to_identify <- c("62aaafe8-f268-5a20-8e3c-8d28afbb9807", "0d022c71-d7bc-50ad-afd3-25a9145ec869",
                    "59d8c37c-a3e1-5615-a44e-869533ddbd31", "ac587605-34f6-5f2f-9a5f-c6c3d6dccac2",
                    "00db9989-a62d-57f3-b25f-6316cd1ce846", "853da6d0-f7ba-5c62-88af-2dc06d5d9d07",
                    "e59d61d0-0582-5076-8401-eee2b980cbdf", "77903714-3207-5a54-a0dd-963bdbf6dcf8",
                    "065565ad-f6a5-5949-84d0-8797a995ccc0", "b954071b-0d60-51a1-811b-b7c8561f3d2c",
                    "bbcc65ed-1393-5023-810f-f9f63c786d9f", "414cf197-29bc-515b-9620-e507c1cadc3e",
                    "735cdcef-e685-5f37-8463-e7cd5637f891", "406ee778-5b0c-5ced-9668-fafc9c21aba9",
                    "4893adc6-1255-5f1c-9795-59bbd70516e3", "1bc76c89-ba2e-5a8a-86c0-21adbc493019",
                    "25297615-57ad-5030-8142-3ca7b4596cc7", "0a367fed-52d7-58d4-812b-341ee5b8b416",
                    "64675dae-37f8-5cac-b60e-1a83eb8b2b1c", "36d14b41-c040-5049-b02d-ff798fc6b7be",
                    "62aaafe8-f268-5a20-8e3c-8d28afbb9807", "0d022c71-d7bc-50ad-afd3-25a9145ec869",
                    "59d8c37c-a3e1-5615-a44e-869533ddbd31", "ac587605-34f6-5f2f-9a5f-c6c3d6dccac2",
                    "00db9989-a62d-57f3-b25f-6316cd1ce846", "853da6d0-f7ba-5c62-88af-2dc06d5d9d07",
                    "e59d61d0-0582-5076-8401-eee2b980cbdf", "77903714-3207-5a54-a0dd-963bdbf6dcf8",
                    "065565ad-f6a5-5949-84d0-8797a995ccc0", "b954071b-0d60-51a1-811b-b7c8561f3d2c",
                    "bbcc65ed-1393-5023-810f-f9f63c786d9f", "414cf197-29bc-515b-9620-e507c1cadc3e",
                    "735cdcef-e685-5f37-8463-e7cd5637f891", "406ee778-5b0c-5ced-9668-fafc9c21aba9",
                    "4893adc6-1255-5f1c-9795-59bbd70516e3", "1bc76c89-ba2e-5a8a-86c0-21adbc493019",
                    "25297615-57ad-5030-8142-3ca7b4596cc7", "0a367fed-52d7-58d4-812b-341ee5b8b416",
                    "64675dae-37f8-5cac-b60e-1a83eb8b2b1c", "36d14b41-c040-5049-b02d-ff798fc6b7be")

identified_rows <- main17[main17$UID %in% id_to_identify, ]

row_to_remove <- c(2760,2761,2762,2763,2764,2765,2766,2767,2768,2769,2770,2771,2772,2773,2774,2775,2776,2777,2778,2779)
modified_df <- main17[-row_to_remove, ]
#check that the 20 repeat Segal id's were removed
identified_rows_post <- modified_df[modified_df$UID %in% id_to_identify, ]

#export updated version of Arts Dataset
st_write(modified_df, "C:/Users/jdean/Documents/GitHub/ARTS/ARTS_main_dataset/v.17.0.0/ARTS_main_dataset.geojson")

